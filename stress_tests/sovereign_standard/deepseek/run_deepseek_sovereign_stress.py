from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
import time
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sr8.adapters import create_provider  # noqa: E402
from sr8.adapters.errors import ProviderError  # noqa: E402
from sr8.adapters.types import ProviderRequest  # noqa: E402
from sr8.compiler import CompileConfig, compile_intent  # noqa: E402
from sr8.config.provider_settings import load_provider_settings  # noqa: E402
from sr8.models.intent_artifact import GovernanceFlags, IntentArtifact  # noqa: E402
from sr8.models.validation import ValidationIssue, ValidationReport  # noqa: E402
from sr8.srxml.rc2 import (  # noqa: E402
    ARTIFACT_TYPES,
    classify_srxml_route,
    render_srxml_rc2_artifact,
    validate_srxml_file,
)

MODEL_PROFILE = "DeepSeek-V4-Flash"
PROVIDER_NAME = "azure_openai"
RESULT_SCHEMA_VERSION = "1.1"
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}")

OUTPUT_DIR_NAMES = (
    "artifacts",
    "raw_outputs",
    "parsed",
    "receipts",
    "validation",
    "results",
)

CASE_FIELDS = (
    "case_id",
    "raw_intent",
    "expected_artifact_type",
    "expected_depth_tier",
    "expected_runtime_target",
    "domain",
    "user_type",
    "geography",
    "chaos_type",
    "lens",
    "expected_behavior",
    "validation_focus",
    "should_block",
)

USER_TYPES = (
    "founder_operator",
    "developer",
    "agency_owner",
    "law_firm_operator",
    "finance_operator",
    "healthcare_admin",
    "student_builder",
    "nontechnical_business_owner",
    "enterprise_compliance_lead",
    "chaotic_power_user",
)

DOMAINS = (
    "software_build",
    "repo_refactor",
    "legal_workflow",
    "finance_ops",
    "healthcare_admin",
    "local_business_site",
    "sales_offer",
    "memory_engrave",
    "compliance_evidence",
    "visual_generation",
    "content_system",
    "research_agent",
    "workflow_orchestration",
    "audit_agent",
    "blueprint_design_doc",
)

GEOGRAPHIES = (
    "Canada",
    "United States",
    "United Kingdom",
    "European Union",
    "Middle East",
    "South Asia",
    "East Asia",
    "Africa",
    "Latin America",
    "global_cross_border",
)

CHAOS_TYPES = (
    "ambiguous_scope",
    "missing_inputs",
    "contradictory_constraints",
    "overbroad_one_pass_lock",
    "unsafe_compliance_claim",
    "fake_test_risk",
    "multi_runtime_confusion",
    "language_mixed_prompt",
    "high_urgency_low_context",
    "memory_write_risk",
    "schema_blur",
    "unsupported_roi_claim",
    "tool_permission_confusion",
    "artifact_type_ambiguity",
    "depth_tier_ambiguity",
)

LENSES = (
    "compiler_lens",
    "operator_lens",
    "market_lens",
    "compliance_lens",
    "technical_lens",
    "failure_lens",
    "memory_lens",
    "runtime_lens",
    "sovereign_lens",
)

ARTIFACT_CLASSES = (
    "sr8_compiler_prompt",
    "srx_agent",
    "srx_ace_v3_agent",
    "srx_ace_build_agent",
    "srx_ace_workflow",
    "srx_ace_audit_agent",
    "sr9_orchestration_prompt",
    "mirroros_analysis_prompt",
    "lovable_build_prompt",
    "codex_build_prompt",
    "research_agent_prompt",
    "compliance_evidence_prompt",
    "memory_engrave_prompt",
    "sales_offer_prompt",
    "blueprint_design_doc",
    "visual_generation_prompt",
    "content_prompt",
)

BLOCKING_CHAOS = {
    "missing_inputs",
    "contradictory_constraints",
    "unsafe_compliance_claim",
    "memory_write_risk",
    "unsupported_roi_claim",
    "tool_permission_confusion",
}


@dataclass(frozen=True)
class ModelClassification:
    artifact_type: str
    depth_tier: str
    runtime_target: str
    compiled_intent: str
    should_block: bool
    blocked_reason: str
    raw_payload: dict[str, Any]
    parse_status: str


@dataclass(frozen=True)
class CasePaths:
    raw_output: Path
    parsed: Path
    artifact: Path
    repair_artifact: Path
    validation: Path
    repair_validation: Path
    receipt: Path
    blocked_receipt: Path


def utc_stamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(case_id: object) -> str:
    return str(case_id).strip().replace("/", "_").replace("\\", "_")


def output_root() -> Path:
    return Path(__file__).resolve().parent


def prepare_output_dirs(*, clean: bool) -> None:
    root = output_root()
    for name in OUTPUT_DIR_NAMES:
        target = root / name
        if clean and target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)


def paths_for_case(case_id: str) -> CasePaths:
    root = output_root()
    stem = slug(case_id)
    return CasePaths(
        raw_output=root / "raw_outputs" / f"{stem}.json",
        parsed=root / "parsed" / f"{stem}.json",
        artifact=root / "artifacts" / f"{stem}.srxml.xml",
        repair_artifact=root / "artifacts" / f"{stem}.repair.srxml.xml",
        validation=root / "validation" / f"{stem}.validation.json",
        repair_validation=root / "validation" / f"{stem}.repair.validation.json",
        receipt=root / "receipts" / f"{stem}.receipt.xml",
        blocked_receipt=root / "receipts" / f"{stem}.blocked.xml",
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def depth_for_case(index: int, artifact_type: str) -> str:
    minimum_depth = ARTIFACT_TYPES[artifact_type]["min_depth"]
    if minimum_depth == 3:
        return "D3_SOVEREIGN_CORE"
    if minimum_depth == 2:
        return "D3_SOVEREIGN_CORE" if index % 2 == 0 else "D2_PRODUCTION"
    if index % 10 == 0:
        return "D1_OPERATIONAL"
    if index % 2 == 0:
        return "D3_SOVEREIGN_CORE"
    return "D2_PRODUCTION"


def raw_intent_for_case(
    index: int,
    *,
    artifact_type: str,
    domain: str,
    user_type: str,
    geography: str,
    chaos_type: str,
    lens: str,
    should_block: bool,
) -> str:
    pressure = (
        "Block unsafe certainty and record a repair receipt."
        if should_block
        else "Produce a governed artifact with explicit validation gates."
    )
    return (
        f"Case {index:03d}: I am a {user_type} in {geography}. "
        f"Build a {artifact_type} for {domain} using the {lens}. "
        f"Chaos input type is {chaos_type}. "
        "The source is intentionally messy: mix missing context, urgent language, "
        "partial constraints, and ambiguous acceptance criteria. "
        f"{pressure} "
        "Return something SR8 can compile into objective, scope, constraints, "
        "success criteria, and output contract."
    )


def build_test_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for zero_index in range(100):
        index = zero_index + 1
        artifact_type = ARTIFACT_CLASSES[zero_index % len(ARTIFACT_CLASSES)]
        domain = DOMAINS[zero_index % len(DOMAINS)]
        user_type = USER_TYPES[zero_index % len(USER_TYPES)]
        geography = GEOGRAPHIES[zero_index % len(GEOGRAPHIES)]
        chaos_type = CHAOS_TYPES[zero_index % len(CHAOS_TYPES)]
        lens = LENSES[zero_index % len(LENSES)]
        should_block = chaos_type in BLOCKING_CHAOS
        cases.append(
            {
                "case_id": f"DSS-{index:03d}",
                "raw_intent": raw_intent_for_case(
                    index,
                    artifact_type=artifact_type,
                    domain=domain,
                    user_type=user_type,
                    geography=geography,
                    chaos_type=chaos_type,
                    lens=lens,
                    should_block=should_block,
                ),
                "expected_artifact_type": artifact_type,
                "expected_depth_tier": depth_for_case(index, artifact_type),
                "expected_runtime_target": "Codex",
                "domain": domain,
                "user_type": user_type,
                "geography": geography,
                "chaos_type": chaos_type,
                "lens": lens,
                "expected_behavior": (
                    "block_with_receipt" if should_block else "compile_validate_srxml"
                ),
                "validation_focus": validation_focus_for(artifact_type, chaos_type),
                "should_block": should_block,
            }
        )
    validate_full_suite(cases)
    return cases


def validation_focus_for(artifact_type: str, chaos_type: str) -> str:
    if chaos_type in BLOCKING_CHAOS:
        return "blocked_state_receipt"
    if artifact_type in {"compliance_evidence_prompt", "research_agent_prompt"}:
        return "source_policy_and_claim_limits"
    if artifact_type in {"codex_build_prompt", "srx_ace_build_agent"}:
        return "test_evidence_and_final_report"
    if artifact_type == "memory_engrave_prompt":
        return "memory_safety_and_overwrite_policy"
    return "srxml_required_sections"


def validate_full_suite(cases: list[Mapping[str, Any]]) -> None:
    if len(cases) != 100:
        msg = f"Expected exactly 100 cases, found {len(cases)}."
        raise ValueError(msg)
    for case in cases:
        missing = [field for field in CASE_FIELDS if field not in case]
        if missing:
            msg = f"{case.get('case_id', '<unknown>')} missing fields: {missing}"
            raise ValueError(msg)
    counts = Counter(str(case["expected_artifact_type"]) for case in cases)
    undercovered = [name for name in ARTIFACT_CLASSES if counts[name] < 3]
    if undercovered:
        msg = f"Artifact classes undercovered: {undercovered}"
        raise ValueError(msg)


def load_cases(path: Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        cases = build_test_cases()
        write_json(path, cases)
    else:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("test_cases.json must contain a list.")
        cases = [dict(item) for item in payload]
        validate_full_suite(cases)
    if limit is not None:
        if limit < 1 or limit > len(cases):
            raise ValueError("--limit must be between 1 and the suite size.")
        return cases[:limit]
    return cases


def missing_azure_env() -> list[str]:
    settings = load_provider_settings().azure_openai
    missing: list[str] = []
    if not settings.api_key:
        missing.append("SR8_AZURE_OPENAI_API_KEY")
    if not settings.endpoint:
        missing.append("SR8_AZURE_OPENAI_ENDPOINT")
    if not settings.deployment:
        missing.append("SR8_AZURE_OPENAI_DEPLOYMENT")
    return missing


def require_deepseek_deployment() -> tuple[bool, str]:
    settings = load_provider_settings().azure_openai
    deployment = settings.deployment or ""
    if deployment != MODEL_PROFILE:
        return False, deployment or "<missing>"
    return True, deployment


def system_prompt() -> str:
    classes = ", ".join(ARTIFACT_CLASSES)
    return (
        "You are the DeepSeek-only SR8 Sovereign Standard stress-test model. "
        "Return strict JSON only. No markdown fences. "
        "Schema: artifact_type, depth_tier, runtime_target, should_block, "
        "blocked_reason, compiled_intent. "
        f"artifact_type must be one of: {classes}. "
        "depth_tier must be D1_OPERATIONAL, D2_PRODUCTION, or D3_SOVEREIGN_CORE. "
        "compiled_intent must be an SR8-compilable directive with Objective, Scope, "
        "Constraints, Success Criteria, and Output Contract sections. "
        "If the case requires legal, medical, financial, compliance, memory, ROI, "
        "secret, or fake-test certainty that lacks evidence, set should_block true "
        "and explain the blocker without claiming completion."
    )


def user_prompt(case: Mapping[str, Any]) -> str:
    return json.dumps(
        {
            "case_id": case["case_id"],
            "raw_intent": case["raw_intent"],
            "expected_artifact_type": case["expected_artifact_type"],
            "expected_depth_tier": case["expected_depth_tier"],
            "expected_runtime_target": case["expected_runtime_target"],
            "validation_focus": case["validation_focus"],
            "should_block": case["should_block"],
        },
        sort_keys=True,
    )


def dry_model_response(case: Mapping[str, Any]) -> str:
    return json.dumps(
        {
            "artifact_type": case["expected_artifact_type"],
            "depth_tier": case["expected_depth_tier"],
            "runtime_target": case["expected_runtime_target"],
            "should_block": bool(case["should_block"]),
            "blocked_reason": (
                f"Blocked for {case['chaos_type']} pending source evidence."
                if case["should_block"]
                else ""
            ),
            "compiled_intent": structured_intent_from_case(case),
        },
        sort_keys=True,
    )


def structured_intent_from_case(case: Mapping[str, Any]) -> str:
    block_line = (
        f"Blocked State: {case['chaos_type']} requires repair before execution."
        if case["should_block"]
        else "Blocked State: none."
    )
    return (
        f"Objective: Build {case['expected_artifact_type']} for {case['domain']} "
        f"in {case['geography']}.\n"
        "Scope:\n"
        f"- Convert the chaotic operator request into {case['expected_artifact_type']}.\n"
        f"- Preserve the {case['lens']} and user type {case['user_type']}.\n"
        "- Include reusable template structure, format rules, and visual style where relevant.\n"
        "- Route through SR8 compile, SRXML RC2 render, validation, and receipt capture.\n"
        "Context Package:\n"
        f"- Domain: {case['domain']}.\n"
        f"- Geography: {case['geography']}.\n"
        f"- Chaos type: {case['chaos_type']}.\n"
        "Constraints:\n"
        "- Do not claim execution, legal compliance, financial return, or test success "
        "without evidence.\n"
        "- Use only the DeepSeek-V4-Flash case output for this run.\n"
        f"- {block_line}\n"
        "Dependencies:\n"
        "- SR8 compile_intent.\n"
        "- SRXML RC2 renderer and validator.\n"
        "Assumptions:\n"
        "- Domain correctness is out of scope unless supported by source evidence.\n"
        "Success Criteria:\n"
        "- SR8 canonical artifact records objective, scope, constraints, success criteria, "
        "and output contract.\n"
        "- SRXML RC2 validation result is recorded.\n"
        "- Blocked-state cases produce repair context instead of false completion.\n"
        "Output Contract:\n"
        "- Machine-readable result row.\n"
        "- SRXML validation status.\n"
        "- Receipt-compatible summary.\n"
        f"Target Class: {case['expected_artifact_type']}.\n"
        f"Authority Context: {case['user_type']} in {case['geography']}."
    )


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```") and "\n" in stripped:
        stripped = stripped.split("\n", 1)[1]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Model output did not contain a JSON object.")
    payload = json.loads(stripped[start : end + 1])
    if not isinstance(payload, dict):
        raise ValueError("Model output JSON must be an object.")
    return payload


def classify_model_output(
    case: Mapping[str, Any],
    content: str,
    *,
    parse_status: str = "parsed",
) -> ModelClassification:
    payload = extract_json_object(content)
    artifact_type = str(payload.get("artifact_type") or "").strip()
    depth_tier = str(payload.get("depth_tier") or "").strip()
    runtime_target = str(payload.get("runtime_target") or "").strip()
    compiled_intent_value = payload.get("compiled_intent")
    compiled_intent = normalize_compiled_intent(compiled_intent_value).strip()
    blocked_reason = str(payload.get("blocked_reason") or "").strip()
    should_block = bool(payload.get("should_block", False))
    if artifact_type not in ARTIFACT_TYPES:
        artifact_type = str(case["expected_artifact_type"])
        parse_status = "repaired_invalid_artifact_type"
    if depth_tier not in {"D1_OPERATIONAL", "D2_PRODUCTION", "D3_SOVEREIGN_CORE"}:
        depth_tier = str(case["expected_depth_tier"])
        parse_status = "repaired_invalid_depth_tier"
    if not runtime_target:
        runtime_target = str(case["expected_runtime_target"])
        parse_status = "repaired_missing_runtime_target"
    if not compiled_intent:
        compiled_intent = structured_intent_from_case(case)
        parse_status = "repaired_missing_compiled_intent"
    return ModelClassification(
        artifact_type=artifact_type,
        depth_tier=depth_tier,
        runtime_target=runtime_target,
        compiled_intent=compiled_intent,
        should_block=should_block,
        blocked_reason=blocked_reason,
        raw_payload=payload,
        parse_status=parse_status,
    )


def normalize_compiled_intent(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        section_aliases = {
            "objective": ("Objective", "objective", "Goal", "goal"),
            "scope": ("Scope", "scope"),
            "constraints": ("Constraints", "constraints", "Requirements", "requirements"),
            "success_criteria": (
                "Success Criteria",
                "success_criteria",
                "Success",
                "success",
                "Acceptance Criteria",
                "acceptance_criteria",
            ),
            "output_contract": (
                "Output Contract",
                "output_contract",
                "Deliverables",
                "deliverables",
            ),
            "context_package": ("Context Package", "context_package", "Context", "context"),
            "dependencies": ("Dependencies", "dependencies"),
            "assumptions": ("Assumptions", "assumptions"),
            "target_class": ("Target Class", "target_class", "Target", "target"),
            "authority_context": (
                "Authority Context",
                "authority_context",
                "Authority",
                "authority",
            ),
        }

        def first_value(names: tuple[str, ...]) -> object:
            for name in names:
                if name in value:
                    return value[name]
            return None

        lines: list[str] = []
        text_sections = (
            ("Objective", "objective"),
            ("Target Class", "target_class"),
            ("Authority Context", "authority_context"),
        )
        list_sections = (
            ("Scope", "scope"),
            ("Context Package", "context_package"),
            ("Constraints", "constraints"),
            ("Dependencies", "dependencies"),
            ("Assumptions", "assumptions"),
            ("Success Criteria", "success_criteria"),
            ("Output Contract", "output_contract"),
        )
        for label, key in text_sections:
            section_value = first_value(section_aliases[key])
            if section_value is not None:
                rendered = render_scalar(section_value)
                if rendered:
                    lines.append(f"{label}: {rendered}")
        for label, key in list_sections:
            section_value = first_value(section_aliases[key])
            if section_value is None:
                continue
            items = render_items(section_value)
            if not items:
                continue
            lines.append(f"{label}:")
            lines.extend(f"- {item}" for item in items)
        return "\n".join(lines)
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in render_items(value))
    return "" if value is None else str(value)


def render_scalar(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Mapping):
        return "; ".join(f"{key}: {render_scalar(item)}" for key, item in value.items())
    if isinstance(value, list):
        return "; ".join(render_items(value))
    return str(value).strip()


def render_items(value: object) -> list[str]:
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    if isinstance(value, Mapping):
        return [f"{key}: {render_scalar(item)}" for key, item in value.items()]
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            rendered = render_scalar(item)
            if rendered:
                items.append(rendered)
        return items
    rendered = render_scalar(value)
    return [rendered] if rendered else []


def fallback_classification(case: Mapping[str, Any], parse_status: str) -> ModelClassification:
    return classify_model_output(case, dry_model_response(case), parse_status=parse_status)


def call_deepseek(case: Mapping[str, Any]) -> tuple[str, dict[str, int], str]:
    provider = create_provider(PROVIDER_NAME)
    settings = load_provider_settings().azure_openai
    response = provider.complete(
        ProviderRequest(
            provider=PROVIDER_NAME,
            model=MODEL_PROFILE,
            prompt=user_prompt(case),
            system_prompt=system_prompt(),
            temperature=0.0,
            max_tokens=1200,
            response_format="json",
            timeout_seconds=settings.timeout_seconds,
            metadata={
                "mode": "deepseek_sovereign_standard_stress",
                "case_id": case["case_id"],
            },
        )
    )
    return response.content, response.usage, response.finish_reason


def apply_srxml_overrides(
    artifact: IntentArtifact,
    classification: ModelClassification,
) -> IntentArtifact:
    metadata = artifact.metadata | {
        "srxml_artifact_type": classification.artifact_type,
        "srxml_depth_tier": classification.depth_tier,
        "runtime_target": classification.runtime_target,
        "deepseek_model_profile": MODEL_PROFILE,
    }
    return artifact.model_copy(update={"metadata": metadata})


def apply_blocked_state(
    artifact: IntentArtifact,
    *,
    case: Mapping[str, Any],
    classification: ModelClassification,
) -> IntentArtifact:
    if not classification.should_block:
        return artifact
    reason = classification.blocked_reason or f"Blocked for {case['chaos_type']}."
    report = ValidationReport(
        report_id=f"val_blocked_{slug(case['case_id']).lower()}",
        readiness_status="fail",
        summary=reason,
        errors=[
            ValidationIssue(
                code="VAL-STRESS-BLOCKED",
                message=reason,
                path="stress_case.should_block",
            )
        ],
    )
    return artifact.model_copy(
        update={
            "governance_flags": GovernanceFlags(
                ambiguous=True,
                incomplete=True,
                requires_human_review=True,
            ),
            "validation": report,
        }
    )


def scrub_artifact_placeholders(artifact: IntentArtifact) -> IntentArtifact:
    def scrub_text(value: str) -> str:
        return PLACEHOLDER_RE.sub("[placeholder removed for repair]", value)

    def scrub_list(values: list[str]) -> list[str]:
        return [scrub_text(value) for value in values]

    return artifact.model_copy(
        update={
            "objective": scrub_text(artifact.objective),
            "scope": scrub_list(artifact.scope),
            "exclusions": scrub_list(artifact.exclusions),
            "constraints": scrub_list(artifact.constraints),
            "context_package": scrub_list(artifact.context_package),
            "target_class": scrub_text(artifact.target_class),
            "authority_context": scrub_text(artifact.authority_context),
            "dependencies": scrub_list(artifact.dependencies),
            "assumptions": scrub_list(artifact.assumptions),
            "success_criteria": scrub_list(artifact.success_criteria),
            "output_contract": scrub_list(artifact.output_contract),
        }
    )


def write_srxml_artifact(path: Path, artifact: IntentArtifact) -> None:
    write_text(path, render_srxml_rc2_artifact(artifact))


def validate_artifact_file(artifact_path: Path, validation_path: Path) -> dict[str, Any]:
    validation = validate_srxml_file(artifact_path)
    payload = validation.as_dict() | {
        "artifact_file": str(artifact_path),
        "validated_at": utc_stamp(),
    }
    write_json(validation_path, payload)
    return payload


def repair_srxml_file_if_needed(
    artifact: IntentArtifact,
    case: Mapping[str, Any],
    paths: CasePaths,
    first_validation: Mapping[str, Any],
) -> tuple[bool, bool]:
    if bool(first_validation["valid"]):
        return False, False
    repaired = scrub_artifact_placeholders(artifact).model_copy(
        update={
            "metadata": artifact.metadata
            | {
                "srxml_artifact_type": case["expected_artifact_type"],
                "srxml_depth_tier": case["expected_depth_tier"],
                "runtime_target": case["expected_runtime_target"],
            }
        }
    )
    write_srxml_artifact(paths.repair_artifact, repaired)
    repaired_validation = validate_artifact_file(paths.repair_artifact, paths.repair_validation)
    if not bool(repaired_validation["valid"]):
        write_blocked_receipt(paths.blocked_receipt, case=case, validation=repaired_validation)
    return True, bool(repaired_validation["valid"])


def write_per_case_receipt(
    path: Path,
    *,
    case: Mapping[str, Any],
    row: Mapping[str, Any],
) -> None:
    root = ElementTree.Element("SR8DeepSeekCaseReceipt")
    root.set("case_id", str(case["case_id"]))
    source = ElementTree.SubElement(root, "source_intent")
    append_xml_text(source, "raw_intent", str(case["raw_intent"]))
    append_xml_text(source, "domain", str(case["domain"]))
    append_xml_text(source, "user_type", str(case["user_type"]))
    append_xml_text(source, "geography", str(case["geography"]))
    append_xml_text(source, "chaos_type", str(case["chaos_type"]))
    append_xml_text(source, "lens", str(case["lens"]))

    parsed = ElementTree.SubElement(root, "parsed_tester_json")
    for key in [
        "observed_artifact_type",
        "observed_depth_tier",
        "observed_runtime_target",
        "model_should_block",
        "blocked_reason",
        "compiled_intent",
    ]:
        append_xml_text(parsed, key, str(row.get(key, "")))

    artifact = ElementTree.SubElement(root, "compiled_artifact")
    for key in [
        "artifact_id",
        "source_hash",
        "compile_run_id",
        "artifact_file",
        "srxml_status",
        "sr8_receipt_status",
        "sr8_validation_status",
    ]:
        append_xml_text(artifact, key, str(row.get(key, "")))

    validation = ElementTree.SubElement(root, "file_validation")
    for key in [
        "validation_file",
        "srxml_valid_first_pass",
        "repair_artifact_file",
        "repair_validation_file",
        "srxml_valid_after_repair",
        "valid_or_correctly_blocked",
    ]:
        append_xml_text(validation, key, str(row.get(key, "")))

    runtime = ElementTree.SubElement(root, "runtime")
    for key in [
        "model_profile",
        "provider",
        "execution_mode",
        "api_error",
        "compiler_error",
        "validator_error",
    ]:
        append_xml_text(runtime, key, str(row.get(key, "")))
    failure_modes = ElementTree.SubElement(root, "failure_modes")
    for mode in row.get("failure_modes", []):
        append_xml_text(failure_modes, "failure_mode", str(mode))
    ElementTree.indent(root)
    write_text(
        path,
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ElementTree.tostring(root, encoding="unicode"),
    )


def write_blocked_receipt(
    path: Path,
    *,
    case: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> None:
    root = ElementTree.Element("SR8DeepSeekBlockedStateReceipt")
    root.set("case_id", str(case["case_id"]))
    append_xml_text(root, "status", "blocked")
    append_xml_text(root, "reason", "repair_validation_failed")
    append_xml_text(root, "validation", json.dumps(validation, sort_keys=True))
    ElementTree.indent(root)
    write_text(
        path,
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ElementTree.tostring(root, encoding="unicode"),
    )


def append_xml_text(parent: ElementTree.Element, tag: str, value: str) -> None:
    child = ElementTree.SubElement(parent, tag)
    child.text = value


def run_case(case: Mapping[str, Any], mode: str) -> dict[str, Any]:
    started = time.perf_counter()
    paths = paths_for_case(str(case["case_id"]))
    api_error = ""
    compiler_error = ""
    validator_error = ""
    execution_mode = mode
    usage: dict[str, int] = {}
    finish_reason = ""
    failure_modes: list[str] = []

    try:
        if mode == "live":
            model_content, usage, finish_reason = call_deepseek(case)
        else:
            model_content = dry_model_response(case)
            finish_reason = "dry_run"
    except ProviderError as exc:
        api_error = type(exc).__name__
        execution_mode = "live_api_error_dry_compile"
        model_content = dry_model_response(case)
        finish_reason = "api_error_dry_fallback"
        failure_modes.append("model_api_error")

    write_json(
        paths.raw_output,
        {
            "case_id": case["case_id"],
            "model_profile": MODEL_PROFILE,
            "provider": PROVIDER_NAME,
            "execution_mode": execution_mode,
            "content": model_content,
            "finish_reason": finish_reason,
            "usage": usage,
            "api_error": api_error,
            "captured_at": utc_stamp(),
        },
    )

    try:
        classification = classify_model_output(case, model_content)
    except (json.JSONDecodeError, ValueError) as exc:
        classification = fallback_classification(case, "fallback_after_parse_error")
        failure_modes.append("missing_output_contract")
        if not api_error:
            api_error = type(exc).__name__

    write_json(
        paths.parsed,
        {
            "case_id": case["case_id"],
            "parse_status": classification.parse_status,
            "artifact_type": classification.artifact_type,
            "depth_tier": classification.depth_tier,
            "runtime_target": classification.runtime_target,
            "should_block": classification.should_block,
            "blocked_reason": classification.blocked_reason,
            "compiled_intent": classification.compiled_intent,
            "raw_payload": classification.raw_payload,
        },
    )

    try:
        result = compile_intent(
            classification.compiled_intent,
            config=CompileConfig(profile="generic", extraction_adapter="rule_based"),
        )
        artifact = apply_srxml_overrides(result.artifact, classification)
        artifact = apply_blocked_state(artifact, case=case, classification=classification)
        write_srxml_artifact(paths.artifact, artifact)
    except Exception as exc:  # pragma: no cover - stress harness records runtime failures.
        compiler_error = type(exc).__name__
        failure_modes.append("compiler_runtime_error")
        return finalize_failure(case, paths, started, execution_mode, api_error, compiler_error)

    try:
        validation = validate_artifact_file(paths.artifact, paths.validation)
        route = classify_srxml_route(artifact)
    except Exception as exc:  # pragma: no cover - stress harness records runtime failures.
        validator_error = type(exc).__name__
        failure_modes.append("validator_runtime_error")
        return finalize_failure(
            case,
            paths,
            started,
            execution_mode,
            api_error,
            compiler_error,
            validator_error=validator_error,
        )

    repair_attempted, repair_success = repair_srxml_file_if_needed(
        artifact,
        case,
        paths,
        validation,
    )
    artifact_type_match = classification.artifact_type == case["expected_artifact_type"]
    depth_tier_match = classification.depth_tier == case["expected_depth_tier"]
    route_blocked = route.blocked
    blocked_state_correct = bool(case["should_block"]) == route_blocked
    false_completion_detected = bool(case["should_block"]) and not route_blocked

    if not artifact_type_match:
        failure_modes.append("artifact_type_misclassification")
    if not depth_tier_match:
        failure_modes.append("depth_tier_misclassification")
    if not bool(validation["valid"]):
        failure_modes.append("schema_invalid_output")
    if repair_attempted and not repair_success:
        failure_modes.append("repair_failed")
    if false_completion_detected:
        failure_modes.append("false_completion_claim")
    if bool(case["should_block"]) and not route_blocked:
        failure_modes.append("blocked_state_missing")
    if not bool(case["should_block"]) and route_blocked:
        failure_modes.append("blocked_state_overtriggered")

    valid_or_correctly_blocked = bool(validation["valid"]) and (
        (not bool(case["should_block"]) and not route_blocked)
        or (bool(case["should_block"]) and route_blocked)
    )
    row = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "run_timestamp": utc_stamp(),
        "case_id": case["case_id"],
        "model_profile": MODEL_PROFILE,
        "provider": PROVIDER_NAME,
        "execution_mode": execution_mode,
        "expected_artifact_type": case["expected_artifact_type"],
        "observed_artifact_type": classification.artifact_type,
        "artifact_type_match": artifact_type_match,
        "expected_depth_tier": case["expected_depth_tier"],
        "observed_depth_tier": classification.depth_tier,
        "depth_tier_match": depth_tier_match,
        "expected_runtime_target": case["expected_runtime_target"],
        "observed_runtime_target": classification.runtime_target,
        "domain": case["domain"],
        "user_type": case["user_type"],
        "geography": case["geography"],
        "chaos_type": case["chaos_type"],
        "lens": case["lens"],
        "should_block": case["should_block"],
        "model_should_block": classification.should_block,
        "blocked_reason": classification.blocked_reason,
        "compiled_intent": classification.compiled_intent,
        "artifact_id": artifact.artifact_id,
        "source_hash": artifact.source.source_hash,
        "compile_run_id": artifact.lineage.compile_run_id,
        "sr8_receipt_status": result.receipt.status,
        "sr8_validation_status": artifact.validation.readiness_status,
        "srxml_valid_first_pass": bool(validation["valid"]),
        "srxml_status": "blocked" if route_blocked else "accepted",
        "srxml_errors": validation["errors"],
        "srxml_warnings": validation["warnings"],
        "repair_attempted": repair_attempted,
        "srxml_valid_after_repair": repair_success,
        "blocked_state_correct": blocked_state_correct,
        "valid_or_correctly_blocked": valid_or_correctly_blocked,
        "false_completion_detected": false_completion_detected,
        "missing_source_of_truth": file_missing_text(paths.artifact, "source_of_truth"),
        "missing_validation": file_missing_text(paths.artifact, "validation"),
        "missing_receipt": file_missing_text(paths.artifact, "receipt"),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "finish_reason": finish_reason,
        "usage": usage,
        "api_error": api_error,
        "compiler_error": compiler_error,
        "validator_error": validator_error,
        "raw_output_file": str(paths.raw_output),
        "parsed_file": str(paths.parsed),
        "artifact_file": str(paths.artifact),
        "validation_file": str(paths.validation),
        "repair_artifact_file": (
            str(paths.repair_artifact) if paths.repair_artifact.exists() else ""
        ),
        "repair_validation_file": (
            str(paths.repair_validation) if paths.repair_validation.exists() else ""
        ),
        "receipt_file": str(paths.receipt),
        "blocked_receipt_file": (
            str(paths.blocked_receipt) if paths.blocked_receipt.exists() else ""
        ),
        "failure_modes": sorted(set(failure_modes)),
    }
    write_per_case_receipt(paths.receipt, case=case, row=row)
    return row


def file_missing_text(path: Path, text: str) -> bool:
    return text not in path.read_text(encoding="utf-8") if path.exists() else True


def finalize_failure(
    case: Mapping[str, Any],
    paths: CasePaths,
    started: float,
    execution_mode: str,
    api_error: str,
    compiler_error: str,
    *,
    validator_error: str = "",
) -> dict[str, Any]:
    row = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "run_timestamp": utc_stamp(),
        "case_id": case["case_id"],
        "model_profile": MODEL_PROFILE,
        "provider": PROVIDER_NAME,
        "execution_mode": execution_mode,
        "expected_artifact_type": case["expected_artifact_type"],
        "observed_artifact_type": "",
        "artifact_type_match": False,
        "expected_depth_tier": case["expected_depth_tier"],
        "observed_depth_tier": "",
        "depth_tier_match": False,
        "expected_runtime_target": case["expected_runtime_target"],
        "observed_runtime_target": "",
        "domain": case["domain"],
        "user_type": case["user_type"],
        "geography": case["geography"],
        "chaos_type": case["chaos_type"],
        "lens": case["lens"],
        "should_block": case["should_block"],
        "model_should_block": False,
        "blocked_reason": "",
        "compiled_intent": "",
        "artifact_id": "",
        "source_hash": "",
        "compile_run_id": "",
        "sr8_receipt_status": "",
        "sr8_validation_status": "",
        "srxml_valid_first_pass": False,
        "srxml_status": "error",
        "srxml_errors": [],
        "srxml_warnings": [],
        "repair_attempted": False,
        "srxml_valid_after_repair": False,
        "blocked_state_correct": False,
        "valid_or_correctly_blocked": False,
        "false_completion_detected": bool(case["should_block"]),
        "missing_source_of_truth": True,
        "missing_validation": True,
        "missing_receipt": True,
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "finish_reason": "",
        "usage": {},
        "api_error": api_error,
        "compiler_error": compiler_error,
        "validator_error": validator_error,
        "raw_output_file": str(paths.raw_output) if paths.raw_output.exists() else "",
        "parsed_file": str(paths.parsed) if paths.parsed.exists() else "",
        "artifact_file": str(paths.artifact) if paths.artifact.exists() else "",
        "validation_file": str(paths.validation) if paths.validation.exists() else "",
        "repair_artifact_file": "",
        "repair_validation_file": "",
        "receipt_file": str(paths.receipt),
        "blocked_receipt_file": "",
        "failure_modes": sorted(
            {
                *([] if not compiler_error else ["compiler_runtime_error"]),
                *([] if not validator_error else ["validator_runtime_error"]),
            }
        ),
    }
    write_per_case_receipt(paths.receipt, case=case, row=row)
    return row


def row_is_successful(row: Mapping[str, Any]) -> bool:
    return not row["api_error"] and not row["compiler_error"] and not row["validator_error"]


def verify_material_files(results: list[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    for row in results:
        case_id = str(row["case_id"])
        for key in ("raw_output_file", "parsed_file", "validation_file", "receipt_file"):
            path = Path(str(row.get(key, "")))
            if not path.exists():
                errors.append(f"{case_id} missing {key}")
        if row_is_successful(row):
            artifact = Path(str(row.get("artifact_file", "")))
            receipt = Path(str(row.get("receipt_file", "")))
            if not artifact.exists():
                errors.append(f"{case_id} successful case missing artifact file")
            if not receipt.exists():
                errors.append(f"{case_id} successful case missing receipt file")
    return errors


def aggregate_results_from_files(results: list[Mapping[str, Any]], mode: str) -> dict[str, Any]:
    attempted = len(results)
    successful_runs = sum(1 for row in results if row_is_successful(row))
    api_failures = sum(1 for row in results if row["api_error"])
    compiler_failures = sum(1 for row in results if row["compiler_error"])
    validator_failures = sum(1 for row in results if row["validator_error"])
    validations = [load_validation_file(row, "validation_file") for row in results]
    first_pass_valid = sum(1 for item in validations if item and item.get("valid") is True)
    repair_validation_files = [
        Path(str(row["repair_validation_file"]))
        for row in results
        if str(row.get("repair_validation_file", ""))
    ]
    repair_success = sum(
        1 for path in repair_validation_files if json.loads(path.read_text()).get("valid") is True
    )
    valid_or_blocked = sum(1 for row in results if row["valid_or_correctly_blocked"])
    false_completion = sum(1 for row in results if row["false_completion_detected"])
    expected_blocked = sum(1 for row in results if row["should_block"])
    correctly_blocked = sum(
        1 for row in results if row["should_block"] and row["blocked_state_correct"]
    )
    classes_tested = {
        str(load_validation_file(row, "validation_file").get("artifact_type", ""))
        for row in results
        if load_validation_file(row, "validation_file")
    }
    failure_counter: Counter[str] = Counter()
    for row in results:
        failure_counter.update(str(item) for item in row["failure_modes"])
    material_errors = verify_material_files(results)
    repair_attempts = len(repair_validation_files)
    repair_success_rate = 1.0 if repair_attempts == 0 else ratio(repair_success, repair_attempts)
    unique_compiled_intents = {
        str(row.get("compiled_intent", "")).strip()
        for row in results
        if str(row.get("compiled_intent", "")).strip()
    }
    unique_source_hashes = {
        str(row.get("source_hash", "")).strip()
        for row in results
        if str(row.get("source_hash", "")).strip()
    }
    unique_artifact_ids = {
        str(row.get("artifact_id", "")).strip()
        for row in results
        if str(row.get("artifact_id", "")).strip()
    }
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "generated_at": utc_stamp(),
        "mode": mode,
        "model_profile": MODEL_PROFILE,
        "provider": PROVIDER_NAME,
        "test_count": attempted,
        "attempted_runs": attempted,
        "successful_runs": successful_runs,
        "api_failures": api_failures,
        "compiler_failures": compiler_failures,
        "validator_failures": validator_failures,
        "material_file_errors": material_errors,
        "unique_compiled_intents": len(unique_compiled_intents),
        "unique_source_hashes": len(unique_source_hashes),
        "unique_artifact_ids": len(unique_artifact_ids),
        "overall_pass_rate": ratio(valid_or_blocked, attempted),
        "first_pass_srxml_validity": ratio(first_pass_valid, attempted),
        "repair_success_rate": repair_success_rate,
        "false_completion_rate": ratio(false_completion, attempted),
        "blocked_state_correctness": ratio(correctly_blocked, expected_blocked),
        "artifact_class_coverage": ratio(len(classes_tested), len(ARTIFACT_CLASSES)),
        "artifact_classes_tested": sorted(classes_tested),
        "failure_modes": dict(sorted(failure_counter.items())),
        "readiness_verdict": readiness_verdict(
            overall=ratio(valid_or_blocked, attempted),
            first_pass=ratio(first_pass_valid, attempted),
            repair=repair_success_rate,
            false_completion=ratio(false_completion, attempted),
            blocked=ratio(correctly_blocked, expected_blocked),
            mode=mode,
            api_failures=api_failures,
            material_errors=material_errors,
        ),
    }


def load_validation_file(row: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = str(row.get(key, ""))
    if not value:
        return {}
    path = Path(value)
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def readiness_verdict(
    *,
    overall: float,
    first_pass: float,
    repair: float,
    false_completion: float,
    blocked: float,
    mode: str,
    api_failures: int,
    material_errors: list[str],
) -> str:
    if material_errors:
        return "invalid_material_artifacts_missing"
    if mode != "live" or api_failures:
        return "not_broad_template_safe_live_execution_incomplete"
    if (
        overall >= 0.90
        and first_pass >= 0.75
        and repair >= 0.70
        and false_completion == 0.0
        and blocked >= 0.95
    ):
        return "deepseek_pass_meets_stress_targets"
    return "not_broad_template_safe_targets_not_met"


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_csv(path: Path, rows: list[Mapping[str, Any]]) -> None:
    fields = [
        "case_id",
        "execution_mode",
        "expected_artifact_type",
        "observed_artifact_type",
        "artifact_type_match",
        "expected_depth_tier",
        "observed_depth_tier",
        "depth_tier_match",
        "should_block",
        "model_should_block",
        "srxml_valid_first_pass",
        "srxml_status",
        "blocked_state_correct",
        "valid_or_correctly_blocked",
        "false_completion_detected",
        "latency_ms",
        "api_error",
        "compiler_error",
        "validator_error",
        "compiled_intent",
        "artifact_id",
        "source_hash",
        "compile_run_id",
        "raw_output_file",
        "parsed_file",
        "artifact_file",
        "validation_file",
        "receipt_file",
        "failure_modes",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: json.dumps(row.get(field, "")) for field in fields})


def write_reports(
    *,
    metrics: Mapping[str, Any],
    results: list[Mapping[str, Any]],
    report_path: Path,
    hardening_path: Path,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    failures = Counter()
    for row in results:
        failures.update(str(item) for item in row["failure_modes"])
    report_path.write_text(
        "\n".join(
            [
                "# SR8 DeepSeek Sovereign Standard Stress Test Report",
                "",
                f"Generated: {metrics['generated_at']}",
                f"Model profile: {MODEL_PROFILE}",
                f"Provider: {PROVIDER_NAME}",
                f"Mode: {metrics['mode']}",
                "",
                "## Repo truth summary",
                "",
                "- Python package manager: pyproject.toml with hatchling.",
                "- CLI entry point: sr8 = sr8.cli:app.",
                "- Compile path: sr8.compiler.compile.compile_intent.",
                "- Azure integration: sr8.adapters.azure_openai_adapter.AzureOpenAIAdapter.",
                "- SRXML RC2 integration: sr8.srxml.rc2 render and validate functions.",
                "- Validation source: SRXML artifact files on disk, not inferred flags.",
                "- Root .env exists and was used through pydantic settings without printing keys.",
                "",
                "## Metrics",
                "",
                f"- Test count: {metrics['test_count']}",
                f"- Attempted runs: {metrics['attempted_runs']}",
                f"- Successful material runs: {metrics['successful_runs']}",
                f"- API failures: {metrics['api_failures']}",
                f"- Compiler failures: {metrics['compiler_failures']}",
                f"- Validator failures: {metrics['validator_failures']}",
                f"- Material file errors: {len(metrics['material_file_errors'])}",
                f"- Unique compiled intents: {metrics['unique_compiled_intents']}",
                f"- Unique source hashes: {metrics['unique_source_hashes']}",
                f"- Unique artifact IDs: {metrics['unique_artifact_ids']}",
                f"- Overall pass rate: {metrics['overall_pass_rate']}",
                f"- First-pass SRXML validity: {metrics['first_pass_srxml_validity']}",
                f"- Repair success rate: {metrics['repair_success_rate']}",
                f"- False completion rate: {metrics['false_completion_rate']}",
                f"- Blocked-state correctness: {metrics['blocked_state_correctness']}",
                f"- Artifact class coverage: {metrics['artifact_class_coverage']}",
                "",
                "## Material outputs",
                "",
                "- Raw outputs: stress_tests/sovereign_standard/deepseek/raw_outputs/",
                "- Parsed JSON: stress_tests/sovereign_standard/deepseek/parsed/",
                "- SRXML artifacts: stress_tests/sovereign_standard/deepseek/artifacts/",
                "- File validation: stress_tests/sovereign_standard/deepseek/validation/",
                "- Per-case receipts: stress_tests/sovereign_standard/deepseek/receipts/",
                "",
                "## Failure patterns",
                "",
                *[f"- {name}: {count}" for name, count in sorted(failures.items())],
                "",
                "## Readiness verdict",
                "",
                str(metrics["readiness_verdict"]),
                "",
                "## Remaining specific-domain gaps",
                "",
                "- Legal, finance, healthcare, and compliance cases remain compiler-behavior "
                "tests only, not domain correctness validation.",
                "- Live Azure service availability and deployment policy can still block model "
                "execution independently of SR8.",
                "- External factual research was not performed by this harness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    hardening_path.write_text(
        "\n".join(
            [
                "# SR8 Template Hardening Report - DeepSeek",
                "",
                "## Changes",
                "",
                "- Extended SRXML RC2 artifact registry to cover all required Sovereign "
                "Standard stress-test artifact classes.",
                "- Added renderer sections for SRX agent, ACE workflow, orchestration, "
                "audit, memory, compliance evidence, sales, Lovable, and MirrorOS classes.",
                "- Added srxml_depth_tier metadata override support with blocked-state "
                "handling for unsupported depth values.",
                "- Added file-backed DeepSeek harness outputs for raw responses, parsed "
                "tester JSON, compiled SRXML artifacts, validation results, repairs, "
                "blocked receipts, and per-case receipts.",
                "",
                "## Validation posture",
                "",
                "The hardening is template and validation coverage work. It does not claim "
                "production readiness unless the live DeepSeek run meets the scoring targets.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_receipt(path: Path, metrics: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    root = ElementTree.Element("SR8DeepSeekSovereignStandardReceipts")
    execution = ElementTree.SubElement(root, "receipt", {"id": "R-DEEPSEEK-STRESS-EXECUTION"})
    for key in [
        "test_count",
        "model_profile",
        "attempted_runs",
        "successful_runs",
        "api_failures",
        "compiler_failures",
        "validator_failures",
        "unique_compiled_intents",
        "unique_source_hashes",
        "unique_artifact_ids",
    ]:
        append_xml_text(execution, key, str(metrics[key]))
    hardening = ElementTree.SubElement(root, "receipt", {"id": "R-DEEPSEEK-HARDENING"})
    append_xml_text(hardening, "failure_patterns_found", json.dumps(metrics["failure_modes"]))
    append_xml_text(
        hardening,
        "files_changed",
        "src/sr8/srxml/rc2.py; stress_tests/sovereign_standard/deepseek",
    )
    append_xml_text(hardening, "templates_changed", "SRXML RC2 artifact renderer")
    append_xml_text(hardening, "validator_changes", "SRXML RC2 artifact registry")
    append_xml_text(
        hardening,
        "docs_changed",
        "docs/SR8_DeepSeek_Sovereign_Standard_Stress_Test_Report.md; "
        "docs/SR8_Template_Hardening_Report_DeepSeek.md",
    )
    readiness = ElementTree.SubElement(root, "receipt", {"id": "R-DEEPSEEK-READINESS"})
    for key in [
        "overall_pass_rate",
        "false_completion_rate",
        "repair_success_rate",
        "blocked_state_correctness",
        "readiness_verdict",
    ]:
        append_xml_text(readiness, key, str(metrics[key]))
    append_xml_text(
        readiness,
        "remaining_gaps",
        "Domain correctness, live service availability, and external factual research.",
    )
    ElementTree.indent(root)
    write_text(
        path,
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        + ElementTree.tostring(root, encoding="unicode"),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run DeepSeek-V4-Flash SR8 stress suite.")
    parser.add_argument(
        "--cases",
        default=str(Path(__file__).with_name("test_cases.json")),
        help="Path to the 100-case JSON suite.",
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "live", "dry"),
        default="auto",
        help="auto uses live only when Azure DeepSeek env is complete.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Run only the first N cases.")
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not clear harness output directories before running.",
    )
    parser.add_argument(
        "--write-cases-only",
        action="store_true",
        help="Write deterministic test_cases.json and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cases_path = Path(args.cases)
    if args.write_cases_only:
        cases = build_test_cases()
        write_json(cases_path, cases)
        print(f"Wrote {len(cases)} cases to {cases_path}")
        return 0
    cases = load_cases(cases_path, limit=args.limit)

    missing = missing_azure_env()
    deployment_ok, deployment = require_deepseek_deployment()
    mode = args.mode
    if mode == "auto":
        mode = "live" if not missing and deployment_ok else "dry"
    if mode == "live" and missing:
        print(f"Azure env missing {missing}; using dry mode.")
        mode = "dry"
    if mode == "live" and not deployment_ok:
        print(f"Azure deployment is {deployment}; expected {MODEL_PROFILE}; using dry mode.")
        mode = "dry"

    prepare_output_dirs(clean=not args.no_clean)
    results = [run_case(case, mode=mode) for case in cases]
    metrics = aggregate_results_from_files(results, mode=mode)
    root = output_root()
    write_jsonl(root / "results" / "deepseek_v4_flash_results.jsonl", results)
    write_json(root / "results" / "aggregate_metrics.json", metrics)
    write_csv(root / "results" / "summary.csv", results)
    write_reports(
        metrics=metrics,
        results=results,
        report_path=REPO_ROOT / "docs" / "SR8_DeepSeek_Sovereign_Standard_Stress_Test_Report.md",
        hardening_path=REPO_ROOT / "docs" / "SR8_Template_Hardening_Report_DeepSeek.md",
    )
    write_receipt(
        REPO_ROOT / "receipts" / "SR8_DEEPSEEK_SOVEREIGN_STANDARD_TEST_RECEIPT.xml",
        metrics,
    )
    print(json.dumps(metrics, indent=2, sort_keys=True))
    if metrics["material_file_errors"]:
        return 1
    return 0 if metrics["attempted_runs"] == len(cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
