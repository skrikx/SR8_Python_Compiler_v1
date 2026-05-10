from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from xml.etree import ElementTree

from sr8.frontdoor.xml_renderer import sanitize_xml_text
from sr8.models.intent_artifact import IntentArtifact

SRXML_NAMESPACE = "https://platxp.ai/srxml/v1"
SRXML_SCHEMA_VERSION = "1.0.0-rc2"

DepthTier = Literal["D0_QUICK", "D1_OPERATIONAL", "D2_PRODUCTION", "D3_SOVEREIGN_CORE"]
FindingSeverity = Literal["fatal", "warning"]

DEPTH_RANK: dict[str, int] = {
    "D0_QUICK": 0,
    "D1_OPERATIONAL": 1,
    "D2_PRODUCTION": 2,
    "D3_SOVEREIGN_CORE": 3,
}

ARTIFACT_TYPES: dict[str, dict[str, object]] = {
    "sr8_compiler_prompt": {
        "min_depth": 1,
        "required": [
            "compiler_identity",
            "raw_intent",
            "artifact_classification",
            "compilation_rules",
            "output_artifact_contract",
        ],
    },
    "codex_build_prompt": {
        "min_depth": 2,
        "required": [
            "repo_context",
            "target_changes",
            "inspection_requirements",
            "implementation_steps",
            "test_commands",
            "validation_gates",
            "final_report",
        ],
    },
    "research_agent_prompt": {
        "min_depth": 2,
        "required": [
            "research_question",
            "source_policy",
            "search_strategy",
            "evidence_standard",
            "synthesis_model",
            "citation_rules",
            "limitations",
            "final_report_contract",
        ],
    },
    "blueprint_design_doc": {
        "min_depth": 2,
        "required": [
            "problem_statement",
            "objectives",
            "system_context",
            "requirements",
            "architecture",
            "data_or_state_model",
            "interfaces",
            "acceptance_criteria",
            "implementation_plan",
            "validation_plan",
        ],
    },
    "visual_generation_prompt": {
        "min_depth": 1,
        "required": [
            "visual_objective",
            "subject",
            "composition",
            "style_direction",
            "lighting",
            "materials_or_texture",
            "negative_constraints",
            "quality_gates",
        ],
    },
    "content_prompt": {
        "min_depth": 0,
        "required": ["content_goal", "audience", "voice", "format"],
    },
}

PROFILE_ARTIFACT_TYPE: dict[str, str] = {
    "code_task_graph": "codex_build_prompt",
    "generic": "content_prompt",
    "media_spec": "visual_generation_prompt",
    "plan": "blueprint_design_doc",
    "prd": "blueprint_design_doc",
    "procedure": "blueprint_design_doc",
    "prompt_pack": "sr8_compiler_prompt",
    "repo_audit": "codex_build_prompt",
    "research_brief": "research_agent_prompt",
    "whitepaper_outline": "research_agent_prompt",
}

PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")


@dataclass(frozen=True)
class SRXMLRoute:
    artifact_type: str
    depth_tier: DepthTier
    runtime_targets: tuple[str, ...]
    status: str
    seal_status: str
    blocked: bool
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class SRXMLValidationFinding:
    rule_id: str
    severity: FindingSeverity
    message: str
    remediation: str
    blocking: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "remediation": self.remediation,
            "blocking": self.blocking,
        }


@dataclass(frozen=True)
class SRXMLValidationResult:
    valid: bool
    artifact_type: str
    depth_tier: str
    template_mode: bool
    errors: tuple[SRXMLValidationFinding, ...]
    warnings: tuple[SRXMLValidationFinding, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "artifact_type": self.artifact_type,
            "depth_tier": self.depth_tier,
            "template_mode": self.template_mode,
            "errors": [error.as_dict() for error in self.errors],
            "warnings": [warning.as_dict() for warning in self.warnings],
        }


def _metadata_string(artifact: IntentArtifact, key: str) -> str:
    value = artifact.metadata.get(key)
    return value.strip() if isinstance(value, str) else ""


def _first_non_empty(values: list[str], fallback: str) -> str:
    for value in values:
        stripped = value.strip()
        if stripped:
            return stripped
    return fallback


def _runtime_targets_for(artifact_type: str, artifact: IntentArtifact) -> tuple[str, ...]:
    targets = ["SR8"]
    metadata_target = _metadata_string(artifact, "runtime_target")
    if metadata_target:
        targets.append(metadata_target)
    if artifact_type in {"codex_build_prompt", "sr8_compiler_prompt"}:
        targets.append("Codex")
    if artifact_type == "visual_generation_prompt":
        targets.append("image_generation_runtime")
    unique: list[str] = []
    for target in targets:
        if target not in unique:
            unique.append(target)
    return tuple(unique)


def classify_srxml_route(artifact: IntentArtifact) -> SRXMLRoute:
    requested = _metadata_string(artifact, "srxml_artifact_type")
    blocked_reasons: list[str] = []
    if requested:
        if requested in ARTIFACT_TYPES:
            artifact_type = requested
        else:
            artifact_type = PROFILE_ARTIFACT_TYPE.get(artifact.profile, "content_prompt")
            blocked_reasons.append(f"Unsupported srxml_artifact_type override: {requested}")
    else:
        artifact_type = PROFILE_ARTIFACT_TYPE.get(artifact.profile, "content_prompt")

    if artifact.validation.readiness_status == "fail":
        blocked_reasons.append("SR8 canonical validation status is fail.")
    if artifact.governance_flags.incomplete:
        blocked_reasons.append("SR8 governance flag marks the artifact incomplete.")
    if artifact.governance_flags.requires_human_review:
        blocked_reasons.append("SR8 governance flag requires human review.")
    if not artifact.objective.strip():
        blocked_reasons.append("SR8 canonical artifact has no objective.")

    blocked = bool(blocked_reasons)
    return SRXMLRoute(
        artifact_type=artifact_type,
        depth_tier="D2_PRODUCTION",
        runtime_targets=_runtime_targets_for(artifact_type, artifact),
        status="draft" if blocked else "release_candidate",
        seal_status="not_sealed",
        blocked=blocked,
        blocked_reasons=tuple(blocked_reasons),
    )


def _append_text(parent: ElementTree.Element, tag: str, value: str) -> ElementTree.Element:
    child = ElementTree.SubElement(parent, tag)
    child.text = sanitize_xml_text(value)
    return child


def _append_items(parent: ElementTree.Element, tag: str, items: list[str]) -> ElementTree.Element:
    container = ElementTree.SubElement(parent, tag)
    normalized = [item.strip() for item in items if item.strip()]
    if not normalized:
        normalized = ["No source-supplied entries."]
    for item in normalized:
        _append_text(container, "item", item)
    return container


def _append_commands(
    parent: ElementTree.Element,
    tag: str,
    commands: list[str],
) -> ElementTree.Element:
    container = ElementTree.SubElement(parent, tag)
    normalized = [command.strip() for command in commands if command.strip()]
    if not normalized:
        normalized = [
            "sr8 validate <artifact-path>",
            "sr8 transform <artifact-path> --to xml_srxml_rc2",
        ]
    for command in normalized:
        _append_text(container, "command", command)
    return container


def _join_items(items: list[str], fallback: str) -> str:
    normalized = [item.strip() for item in items if item.strip()]
    return "; ".join(normalized) if normalized else fallback


def _artifact_version(artifact: IntentArtifact) -> str:
    value = artifact.artifact_version.strip()
    if re.fullmatch(r"\d+\.\d+\.\d+(-[a-z0-9.]+)?", value):
        return value
    return "1.0.0"


def _append_metadata(
    root: ElementTree.Element,
    artifact: IntentArtifact,
    route: SRXMLRoute,
) -> None:
    metadata = ElementTree.SubElement(root, "metadata")
    _append_text(metadata, "artifact_id", artifact.artifact_id.lower())
    _append_text(metadata, "artifact_type", route.artifact_type)
    _append_text(
        metadata,
        "title",
        _first_non_empty([artifact.objective], f"SR8 {artifact.profile} artifact"),
    )
    _append_text(metadata, "version", _artifact_version(artifact))
    _append_text(metadata, "status", route.status)
    _append_text(metadata, "depth_tier", route.depth_tier)
    runtime_targets = ElementTree.SubElement(metadata, "runtime_targets")
    for runtime_target in route.runtime_targets:
        _append_text(runtime_targets, "runtime_target", runtime_target)


def _append_core_contract(
    root: ElementTree.Element,
    artifact: IntentArtifact,
    route: SRXMLRoute,
) -> None:
    identity = ElementTree.SubElement(root, "identity")
    _append_text(identity, "operator", "SR8 Compiler")
    _append_text(identity, "system", "SR8")
    _append_text(identity, "role", "SRXML RC2 artifact emitter")
    _append_text(
        identity,
        "authority",
        artifact.authority_context or "Local-first deterministic compilation path.",
    )

    mission = ElementTree.SubElement(root, "mission")
    _append_text(mission, "primary_objective", artifact.objective or "Repair SR8 intent intake.")
    _append_text(
        mission,
        "success_definition",
        _join_items(
            artifact.success_criteria,
            "SRXML artifact validates and records compile receipt state.",
        ),
    )

    scope = ElementTree.SubElement(root, "scope")
    _append_items(scope, "in_scope", artifact.scope or ["SR8 canonical artifact conversion"])
    _append_items(scope, "out_of_scope", artifact.exclusions or ["Final sealed SRXML v1 claim"])
    _append_text(scope, "scope_lock", "one_pass_lock")

    source_of_truth = ElementTree.SubElement(root, "source_of_truth")
    primary_sources = ElementTree.SubElement(source_of_truth, "primary_sources")
    source = ElementTree.SubElement(primary_sources, "source")
    source.set("type", artifact.source.source_type)
    _append_text(source, "name", "SR8 canonical artifact")
    _append_text(source, "source_id", artifact.source.source_id)
    _append_text(source, "source_hash", artifact.source.source_hash)
    _append_text(source, "artifact_id", artifact.artifact_id)
    _append_text(source, "compile_run_id", artifact.lineage.compile_run_id)
    if artifact.source.origin:
        _append_text(source, "origin", artifact.source.origin)
    _append_text(source, "priority", "primary")
    conflict_resolution = ElementTree.SubElement(source_of_truth, "conflict_resolution")
    _append_text(
        conflict_resolution,
        "rule",
        "SR8 canonical artifact fields override renderer defaults.",
    )
    _append_text(
        conflict_resolution,
        "rule",
        "SRXML validation failures force blocked receipt state.",
    )

    input_contract = ElementTree.SubElement(root, "input_contract")
    required_inputs = ElementTree.SubElement(input_contract, "required_inputs")
    input_node = ElementTree.SubElement(required_inputs, "input")
    _append_text(input_node, "name", "sr8_canonical_artifact")
    _append_text(input_node, "type", "IntentArtifact")
    _append_text(input_node, "validation_rule", "Must pass Pydantic IntentArtifact loading.")
    _append_text(input_contract, "missing_input_behavior", "block_with_repair_receipt")

    execution_contract = ElementTree.SubElement(root, "execution_contract")
    _append_text(execution_contract, "runtime", "SR8")
    _append_text(execution_contract, "execution_mode", "deterministic_transform")
    _append_text(
        execution_contract,
        "pipeline",
        "raw_intent -> SR8 classification -> canonical artifact -> "
        "SRXML draft -> SRXML validation -> receipt",
    )

    constraints = ElementTree.SubElement(root, "constraints")
    _append_items(
        constraints,
        "hard_constraints",
        [
            "Preserve source_hash and compile_run_id.",
            "Do not claim final sealed state from RC2 transform output.",
            "Return blocked-state receipt when SR8 readiness is fail or intake is incomplete.",
        ],
    )
    _append_items(
        constraints,
        "forbidden_patterns",
        [
            "fake_validation_success",
            "arbitrary_local_filesystem_read",
            "sealed_claim_without_corpus",
        ],
    )

    gates = ElementTree.SubElement(root, "acceptance_gates")
    gate_inputs = artifact.success_criteria or ["SRXML validates under RC2 static contract."]
    for index, criterion in enumerate(gate_inputs, start=1):
        gate = ElementTree.SubElement(gates, "gate")
        gate.set("id", f"G{index}")
        _append_text(gate, "name", f"SR8 acceptance gate {index}")
        _append_text(gate, "type", "validation")
        _append_text(gate, "pass_condition", criterion)
        _append_text(gate, "failure_condition", "Blocked-state receipt is required.")

    output_contract = ElementTree.SubElement(root, "output_contract")
    _append_text(output_contract, "format", "SRXML 1.0 RC2 XML")
    _append_items(
        output_contract,
        "required_sections",
        [
            "metadata",
            "mission",
            "scope",
            "source_of_truth",
            "validation",
            "failure_handling",
            "receipt",
            "versioning",
        ],
    )
    _append_text(
        output_contract,
        "completion_definition",
        "Artifact parses as XML and passes SRXML RC2 static validation.",
    )


def _append_content_prompt(root: ElementTree.Element, artifact: IntentArtifact) -> None:
    _append_text(root, "content_goal", artifact.objective or "Compile source intent into content.")
    _append_text(root, "audience", artifact.authority_context or "operator")
    _append_text(root, "voice", "direct technical")
    _append_text(root, "format", _join_items(artifact.output_contract, "SRXML RC2 artifact"))


def _append_sr8_compiler_prompt(root: ElementTree.Element, artifact: IntentArtifact) -> None:
    _append_text(root, "compiler_identity", "SR8 local-first intent compiler")
    _append_text(
        root,
        "raw_intent",
        str(artifact.metadata.get("raw_content") or artifact.objective or "Canonical SR8 artifact"),
    )
    classification = ElementTree.SubElement(root, "artifact_classification")
    _append_text(classification, "profile", artifact.profile)
    _append_text(classification, "target_class", artifact.target_class or artifact.profile)
    _append_text(
        classification,
        "compile_kind",
        str(artifact.metadata.get("compile_kind", "unknown")),
    )
    _append_items(
        root,
        "compilation_rules",
        [
            "Preserve source lineage.",
            "Reject incomplete intake with a repair receipt.",
            "Validate before downstream execution.",
        ],
    )
    _append_items(root, "output_artifact_contract", artifact.output_contract or ["SRXML RC2 XML"])


def _append_codex_build_prompt(root: ElementTree.Element, artifact: IntentArtifact) -> None:
    repo_context = ElementTree.SubElement(root, "repo_context")
    _append_text(repo_context, "profile", artifact.profile)
    _append_text(repo_context, "target_class", artifact.target_class or "repo_task")
    _append_text(repo_context, "source_hash", artifact.source.source_hash)
    _append_items(root, "target_changes", artifact.scope or [artifact.objective])
    _append_items(
        root,
        "inspection_requirements",
        artifact.context_package or ["Inspect repository structure and relevant entry points."],
    )
    _append_items(
        root,
        "implementation_steps",
        artifact.dependencies or artifact.scope or ["Implement the canonical SR8 objective."],
    )
    _append_commands(root, "test_commands", ["pytest", "ruff check .", "mypy src"])
    _append_items(
        root,
        "validation_gates",
        artifact.success_criteria or ["Relevant tests pass or blocked state is documented."],
    )
    final_report = ElementTree.SubElement(root, "final_report")
    _append_items(
        final_report,
        "must_include",
        ["changed_files", "commands_run", "validation_result", "receipt_status"],
    )


def _append_research_agent_prompt(root: ElementTree.Element, artifact: IntentArtifact) -> None:
    _append_text(root, "research_question", artifact.objective or "Research source intent.")
    _append_text(root, "source_policy", "Use declared SR8 source_of_truth first.")
    _append_text(
        root,
        "search_strategy",
        _join_items(artifact.scope, "Analyze supplied source context."),
    )
    _append_text(root, "evidence_standard", "Record evidence limits and cite available sources.")
    _append_text(root, "synthesis_model", "Structured findings with explicit uncertainty.")
    _append_text(
        root,
        "citation_rules",
        "Cite every external claim when external research is used.",
    )
    _append_text(
        root,
        "limitations",
        _join_items(artifact.assumptions, "No external corpus guaranteed."),
    )
    _append_text(
        root,
        "final_report_contract",
        _join_items(artifact.output_contract, "Research brief."),
    )


def _append_blueprint_design_doc(root: ElementTree.Element, artifact: IntentArtifact) -> None:
    _append_text(root, "problem_statement", artifact.objective or "Define the system problem.")
    _append_items(
        root,
        "objectives",
        [artifact.objective] if artifact.objective else artifact.scope,
    )
    _append_text(
        root,
        "system_context",
        artifact.authority_context
        or _join_items(artifact.context_package, "SR8 canonical artifact"),
    )
    _append_items(root, "requirements", artifact.scope or ["Satisfy the compiled objective."])
    _append_text(root, "architecture", artifact.target_class or artifact.profile)
    _append_text(root, "data_or_state_model", f"source_hash={artifact.source.source_hash}")
    _append_items(root, "interfaces", artifact.dependencies or ["SR8 CLI and Python API"])
    _append_items(
        root,
        "acceptance_criteria",
        artifact.success_criteria or ["Validation passes under SR8 and SRXML contracts."],
    )
    _append_items(root, "implementation_plan", artifact.scope or ["Execute the compiled plan."])
    _append_items(root, "validation_plan", artifact.output_contract or ["Run SR8 validation."])


def _append_visual_generation_prompt(root: ElementTree.Element, artifact: IntentArtifact) -> None:
    _append_text(root, "visual_objective", artifact.objective or "Generate a visual artifact.")
    _append_text(
        root,
        "subject",
        _join_items(artifact.scope, artifact.target_class or "visual subject"),
    )
    _append_text(root, "composition", "Clear subject-first composition.")
    _append_text(
        root,
        "style_direction",
        artifact.authority_context or "domain-appropriate visual style",
    )
    _append_text(root, "lighting", "balanced lighting")
    _append_text(
        root,
        "materials_or_texture",
        _join_items(artifact.context_package, "not specified"),
    )
    _append_items(
        root,
        "negative_constraints",
        artifact.exclusions or ["No unsafe or unrelated content."],
    )
    _append_items(
        root,
        "quality_gates",
        artifact.success_criteria or ["Meets requested output contract."],
    )


def _append_family_fields(
    root: ElementTree.Element,
    artifact: IntentArtifact,
    route: SRXMLRoute,
) -> None:
    if route.artifact_type == "content_prompt":
        _append_content_prompt(root, artifact)
    elif route.artifact_type == "sr8_compiler_prompt":
        _append_sr8_compiler_prompt(root, artifact)
    elif route.artifact_type == "codex_build_prompt":
        _append_codex_build_prompt(root, artifact)
    elif route.artifact_type == "research_agent_prompt":
        _append_research_agent_prompt(root, artifact)
    elif route.artifact_type == "blueprint_design_doc":
        _append_blueprint_design_doc(root, artifact)
    elif route.artifact_type == "visual_generation_prompt":
        _append_visual_generation_prompt(root, artifact)
    else:
        _append_content_prompt(root, artifact)


def _append_validation_and_receipt(
    root: ElementTree.Element,
    artifact: IntentArtifact,
    route: SRXMLRoute,
) -> None:
    validation = ElementTree.SubElement(root, "validation")
    _append_text(validation, "validation_required", "true")
    methods = ElementTree.SubElement(validation, "methods")
    _append_text(methods, "method", "sr8.validate_artifact")
    _append_text(methods, "method", "sr8.srxml.validate_srxml_text")
    _append_text(
        validation,
        "minimum_pass_standard",
        "SR8 canonical validation must be recorded and SRXML static validation must pass.",
    )
    validation_summary = ElementTree.SubElement(validation, "validation_summary")
    _append_text(validation_summary, "sr8_readiness_status", artifact.validation.readiness_status)
    _append_text(validation_summary, "sr8_report_id", artifact.validation.report_id)
    _append_text(validation_summary, "sr8_summary", artifact.validation.summary)

    failure = ElementTree.SubElement(root, "failure_handling")
    _append_items(
        failure,
        "known_failure_modes",
        [
            "SR8 canonical validation fails.",
            "SR8 artifact classification cannot be represented by SRXML RC2.",
            "SRXML static validation fails after rendering.",
        ],
    )
    _append_text(
        failure,
        "fallback_behavior",
        "Return a blocked-state receipt and repair prompt instead of claiming executable success.",
    )
    blocked_text = (
        "; ".join(route.blocked_reasons)
        if route.blocked_reasons
        else "No blocked state recorded by SR8 at render time."
    )
    _append_text(failure, "blocked_state", blocked_text)

    if route.blocked:
        repair_prompt = ElementTree.SubElement(root, "repair_prompt")
        _append_items(repair_prompt, "required_repairs", list(route.blocked_reasons))
        _append_text(
            repair_prompt,
            "resume_instruction",
            "Repair canonical SR8 fields and rerun transform.",
        )

    receipt = ElementTree.SubElement(root, "receipt")
    _append_text(receipt, "receipt_required", "true")
    _append_text(receipt, "receipt_type", "sr8_transform_receipt")
    _append_text(receipt, "receipt_type", "srxml_validation_receipt")
    _append_text(receipt, "artifact_id", artifact.artifact_id)
    _append_text(receipt, "source_hash", artifact.source.source_hash)
    _append_text(receipt, "compile_run_id", artifact.lineage.compile_run_id)
    _append_text(receipt, "seal_status", route.seal_status)
    _append_text(receipt, "status", "blocked" if route.blocked else "ready_for_validation")
    _append_text(receipt, "must_record", "changed files, commands run, validation result, lineage")

    versioning = ElementTree.SubElement(root, "versioning")
    _append_text(versioning, "semver", _artifact_version(artifact))
    _append_text(versioning, "source_schema_version", artifact.artifact_version)
    _append_text(versioning, "srxml_schema_version", SRXML_SCHEMA_VERSION)


def render_srxml_rc2_artifact(artifact: IntentArtifact) -> str:
    route = classify_srxml_route(artifact)
    root = ElementTree.Element(
        "SRXML_Artifact",
        {
            "xmlns": SRXML_NAMESPACE,
            "schema_version": SRXML_SCHEMA_VERSION,
            "emitted_by": "sr8",
        },
    )
    _append_metadata(root, artifact, route)
    _append_core_contract(root, artifact, route)
    _append_family_fields(root, artifact, route)
    _append_validation_and_receipt(root, artifact, route)
    payload = ElementTree.tostring(root, encoding="unicode")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{payload}'


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _children(root: ElementTree.Element | None, name: str) -> list[ElementTree.Element]:
    if root is None:
        return []
    return [element for element in root.iter() if _strip_ns(element.tag) == name]


def _find(root: ElementTree.Element, path: str) -> ElementTree.Element | None:
    current: ElementTree.Element | None = root
    for part in path.split("."):
        if current is None:
            return None
        found = None
        for child in list(current):
            if _strip_ns(child.tag) == part:
                found = child
                break
        current = found
    return current


def _text_of(root: ElementTree.Element, path: str) -> str:
    node = _find(root, path)
    return "".join(node.itertext()).strip() if node is not None else ""


def _exists(root: ElementTree.Element, path: str) -> bool:
    return _text_of(root, path) != ""


def _any_tag(root: ElementTree.Element, name: str) -> bool:
    return bool(_children(root, name))


def _add_finding(
    findings: list[SRXMLValidationFinding],
    rule_id: str,
    severity: FindingSeverity,
    message: str,
    remediation: str,
) -> None:
    findings.append(
        SRXMLValidationFinding(
            rule_id=rule_id,
            severity=severity,
            message=message,
            remediation=remediation,
            blocking=severity == "fatal",
        )
    )


def validate_srxml_text(xml_text: str) -> SRXMLValidationResult:
    errors: list[SRXMLValidationFinding] = []
    warnings: list[SRXMLValidationFinding] = []
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        finding = SRXMLValidationFinding(
            rule_id="XML-PARSE",
            severity="fatal",
            message=str(exc),
            remediation="Fix XML well-formedness.",
            blocking=True,
        )
        return SRXMLValidationResult(
            valid=False,
            artifact_type="",
            depth_tier="",
            template_mode=False,
            errors=(finding,),
            warnings=(),
        )

    template_mode = root.attrib.get("template_mode", "false").lower() == "true"
    artifact_type = _text_of(root, "metadata.artifact_type")
    depth_tier = _text_of(root, "metadata.depth_tier")
    rank = DEPTH_RANK.get(depth_tier)

    required_metadata = [
        ("metadata.artifact_id", "L-MISSING_ARTIFACT_ID"),
        ("metadata.artifact_type", "L-MISSING_ARTIFACT_TYPE"),
        ("metadata.title", "L-MISSING_TITLE"),
        ("metadata.version", "L-MISSING_VERSION"),
        ("metadata.status", "L-MISSING_STATUS"),
        ("metadata.depth_tier", "L-MISSING_DEPTH_TIER"),
    ]
    for path, rule_id in required_metadata:
        if not _exists(root, path):
            _add_finding(errors, rule_id, "fatal", f"Missing {path}.", f"Add {path}.")

    metadata = _find(root, "metadata")
    if not _children(metadata, "runtime_target") and not _exists(
        root, "metadata.runtime_targets.runtime_target"
    ):
        _add_finding(
            errors,
            "L-MISSING_RUNTIME_TARGETS",
            "fatal",
            "metadata.runtime_targets/runtime_target[] is required in RC2.",
            "Add metadata.runtime_targets with at least one runtime_target.",
        )
    if artifact_type and artifact_type not in ARTIFACT_TYPES:
        _add_finding(
            errors,
            "L-UNKNOWN_ARTIFACT_TYPE",
            "fatal",
            f"Unknown artifact_type {artifact_type}.",
            "Use registered artifact_type.",
        )
    if rank is None and depth_tier:
        _add_finding(
            errors,
            "L-UNKNOWN_DEPTH",
            "fatal",
            f"Unknown depth_tier {depth_tier}.",
            "Use D0_QUICK, D1_OPERATIONAL, D2_PRODUCTION, D3_SOVEREIGN_CORE.",
        )

    for path in [
        "mission.primary_objective",
        "mission.success_definition",
        "scope.in_scope",
        "scope.out_of_scope",
        "scope.scope_lock",
        "output_contract.format",
        "output_contract.completion_definition",
    ]:
        if not _exists(root, path):
            _add_finding(
                errors,
                "L-MISSING_ALWAYS_REQUIRED",
                "fatal",
                f"Missing always-required path {path}.",
                f"Add {path}.",
            )

    if rank is not None and rank >= 1:
        for tag in [
            "identity",
            "input_contract",
            "execution_contract",
            "constraints",
            "acceptance_gates",
        ]:
            if not _any_tag(root, tag):
                _add_finding(
                    errors,
                    "L-MISSING_D1_SECTION",
                    "fatal",
                    f"Missing D1+ section {tag}.",
                    f"Add {tag}.",
                )
    if rank is not None and rank >= 2:
        for tag in ["source_of_truth", "validation", "failure_handling", "receipt", "versioning"]:
            if not _any_tag(root, tag):
                _add_finding(
                    errors,
                    "L-MISSING_D2_SECTION",
                    "fatal",
                    f"Missing D2+ section {tag}.",
                    f"Add {tag}.",
                )
        if not _exists(root, "source_of_truth.primary_sources"):
            _add_finding(
                errors,
                "L-MISSING_SOURCE_OF_TRUTH_D2_PLUS",
                "fatal",
                "D2+ requires source_of_truth.primary_sources.",
                "Add source_of_truth primary sources.",
            )
        if not _any_tag(root, "blocked_state"):
            _add_finding(
                errors,
                "L-MISSING_FAILURE_HANDLING_D2_D3",
                "fatal",
                "D2+ requires failure_handling.blocked_state.",
                "Add blocked_state.",
            )
        if not _any_tag(root, "receipt_type"):
            _add_finding(
                errors,
                "L-MISSING_RECEIPT_D2_PLUS",
                "fatal",
                "D2+ requires receipt.receipt_type.",
                "Add receipt_type.",
            )
        if not _any_tag(root, "semver"):
            _add_finding(
                errors,
                "L-MISSING_VERSIONING_D2_PLUS",
                "fatal",
                "D2+ requires versioning.semver.",
                "Add semver.",
            )

    if artifact_type in ARTIFACT_TYPES:
        family = ARTIFACT_TYPES[artifact_type]
        minimum_depth = family["min_depth"]
        if isinstance(minimum_depth, int) and rank is not None and rank < minimum_depth:
            _add_finding(
                errors,
                "L-DEPTH_BELOW_FAMILY_MINIMUM",
                "fatal",
                f"{artifact_type} requires minimum depth rank {minimum_depth}.",
                "Raise depth tier.",
            )
        required_fields = family["required"]
        if isinstance(required_fields, list):
            for tag in required_fields:
                if isinstance(tag, str) and not _any_tag(root, tag):
                    _add_finding(
                        errors,
                        "L-FAMILY_REQUIRED_MISSING",
                        "fatal",
                        f"Missing family-required field {tag} for {artifact_type}.",
                        f"Add {tag}.",
                    )

    if PLACEHOLDER_RE.search(xml_text):
        if template_mode:
            _add_finding(
                warnings,
                "W-TEMPLATE_PLACEHOLDER",
                "warning",
                "Template contains placeholders; allowed because template_mode=true.",
                "Resolve placeholders before execution.",
            )
        else:
            _add_finding(
                errors,
                "L-PLACEHOLDER_IN_NORMAL_ARTIFACT",
                "fatal",
                "Unresolved placeholder found in normal artifact.",
                "Resolve placeholders or set template_mode=true.",
            )

    lower = xml_text.lower()
    if (
        artifact_type == "codex_build_prompt"
        and "tests passed" in lower
        and not _any_tag(root, "test_evidence")
    ):
        _add_finding(
            errors,
            "L-TESTS_PASSED_WITHOUT_EVIDENCE",
            "fatal",
            "Test pass claim lacks evidence.",
            "Add validation.test_evidence or remove claim.",
        )

    return SRXMLValidationResult(
        valid=not any(error.blocking for error in errors),
        artifact_type=artifact_type,
        depth_tier=depth_tier,
        template_mode=template_mode,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )


def validate_srxml_file(path: str | Path) -> SRXMLValidationResult:
    return validate_srxml_text(Path(path).read_text(encoding="utf-8"))
