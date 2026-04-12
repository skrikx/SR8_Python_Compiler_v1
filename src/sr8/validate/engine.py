from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from sr8.extract.trace import coerce_extraction_trace
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.validation import ValidationIssue, ValidationReport
from sr8.profiles.registry import get_profile
from sr8.validate.report import build_validation_report
from sr8.validate.rules import CANONICAL_RULES, execute_rules

TRUST_WARNING_FIELDS = (
    "authority_context",
    "dependencies",
    "assumptions",
    "success_criteria",
    "output_contract",
    "context_package",
)
SEMANTIC_MATERIAL_FIELDS = {"scope", "constraints", "success_criteria", "output_contract"}


def _metadata_list(artifact: IntentArtifact, key: str) -> list[str]:
    value = artifact.metadata.get(key)
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _build_trust_warnings(artifact: IntentArtifact) -> list[ValidationIssue]:
    raw_trace = cast(Mapping[str, object] | None, artifact.metadata.get("extraction_trace"))
    trace = coerce_extraction_trace(raw_trace)
    if trace is None:
        return []

    by_field = {signal.field_name: signal for signal in trace.confidence}
    warnings: list[ValidationIssue] = []
    for index, field_name in enumerate(TRUST_WARNING_FIELDS, start=1):
        signal = by_field.get(field_name)
        if signal is None or signal.status not in {"weak", "contradictory"}:
            continue
        warnings.append(
            ValidationIssue(
                code=f"VAL-TRUST-{index:03d}",
                message=(
                    f"{field_name} extraction trust is {signal.status}; "
                    "downstream output may need manual review"
                ),
                severity="warning",
                path=field_name,
            )
        )

    if artifact.governance_flags.requires_human_review:
        warnings.append(
            ValidationIssue(
                code="VAL-TRUST-900",
                message="governance flags require human review before downstream use",
                severity="warning",
                path="governance_flags.requires_human_review",
            )
        )
    return warnings


def _build_recovery_warnings(artifact: IntentArtifact) -> list[ValidationIssue]:
    raw_recovery = artifact.metadata.get("weak_intent_recovery")
    if not isinstance(raw_recovery, Mapping):
        return []
    intake_required = bool(raw_recovery.get("intake_required"))
    recovery_applied = bool(raw_recovery.get("recovery_applied"))
    if not intake_required and not recovery_applied:
        return []
    missing_fields = raw_recovery.get("missing_fields")
    recovered_fields = raw_recovery.get("recovered_fields")
    weak_fields = raw_recovery.get("weak_fields")
    prompt = raw_recovery.get("suggested_prompt")
    details: list[str] = []
    if isinstance(missing_fields, list) and missing_fields:
        details.append(f"missing={', '.join(str(item) for item in missing_fields)}")
    if isinstance(recovered_fields, list) and recovered_fields:
        details.append(f"recovered={', '.join(str(item) for item in recovered_fields)}")
    if isinstance(weak_fields, list) and weak_fields:
        details.append(f"weak={', '.join(str(item) for item in weak_fields)}")
    suffix = f" ({'; '.join(details)})" if details else ""
    message = "semantic recovery derived missing intent fields"
    prompt_suffix = ""
    if intake_required:
        message = "weak intent recovery path is active"
        prompt_suffix = f" Prompt: {prompt}" if isinstance(prompt, str) and prompt else ""
    return [
        ValidationIssue(
            code="VAL-REC-001",
            message=f"{message}{suffix}.{prompt_suffix}".strip(),
            severity="warning",
            path="metadata.weak_intent_recovery",
        )
    ]


def _build_compile_route_issues(artifact: IntentArtifact) -> list[ValidationIssue]:
    compile_kind = artifact.metadata.get("compile_kind")
    if not isinstance(compile_kind, str) or not compile_kind:
        return []

    derived_fields = set(_metadata_list(artifact, "compiler_derived_fields"))
    source_structure_kind = str(artifact.metadata.get("source_structure_kind", ""))
    semantic_transform_applied = bool(
        artifact.metadata.get("semantic_transform_applied", False)
    )
    issues: list[ValidationIssue] = []

    if compile_kind == "semantic_compile":
        if not semantic_transform_applied:
            issues.append(
                ValidationIssue(
                    code="VAL-ROUTE-001",
                    message="semantic_compile requires a real semantic transform",
                    severity="error",
                    path="metadata.semantic_transform_applied",
                )
            )
        material_derived_fields = derived_fields & SEMANTIC_MATERIAL_FIELDS
        if artifact.source.source_type in {"text", "markdown"} and len(material_derived_fields) < 2:
            issues.append(
                ValidationIssue(
                    code="VAL-ROUTE-002",
                    message=(
                        "semantic_compile on raw text or markdown must derive at least two of "
                        "scope, constraints, success_criteria, or output_contract"
                    ),
                    severity="error",
                    path="metadata.compiler_derived_fields",
                )
            )

    if compile_kind == "canonicalize_structured" and semantic_transform_applied:
        issues.append(
            ValidationIssue(
                code="VAL-ROUTE-003",
                message="canonicalize_structured cannot claim semantic transform was applied",
                severity="error",
                path="metadata.semantic_transform_applied",
            )
        )

    if compile_kind == "needs_intake":
        issues.append(
            ValidationIssue(
                code="VAL-ROUTE-004",
                message=(
                    f"compile route requires intake for {source_structure_kind or 'this source'} "
                    "before downstream use"
                ),
                severity="error",
                path="metadata.compile_kind",
            )
        )
    return issues


def validate_artifact(
    artifact: IntentArtifact,
    profile_name: str | None = None,
) -> ValidationReport:
    active_profile_name = profile_name or artifact.profile or "generic"
    profile = get_profile(active_profile_name)

    canonical_errors, canonical_warnings = execute_rules(artifact, CANONICAL_RULES)
    profile_errors, profile_warnings = profile.validate(artifact)
    trust_warnings = _build_trust_warnings(artifact)
    recovery_warnings = _build_recovery_warnings(artifact)
    route_issues = _build_compile_route_issues(artifact)

    route_errors = [issue for issue in route_issues if issue.severity == "error"]
    route_warnings = [issue for issue in route_issues if issue.severity == "warning"]
    all_errors = canonical_errors + profile_errors + route_errors
    all_warnings = (
        canonical_warnings
        + profile_warnings
        + trust_warnings
        + recovery_warnings
        + route_warnings
    )
    return build_validation_report(
        artifact_id=artifact.artifact_id,
        source_hash=artifact.source.source_hash,
        errors=all_errors,
        warnings=all_warnings,
    )
