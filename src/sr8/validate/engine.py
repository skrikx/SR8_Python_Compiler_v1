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


def validate_artifact(
    artifact: IntentArtifact,
    profile_name: str | None = None,
) -> ValidationReport:
    active_profile_name = profile_name or artifact.profile or "generic"
    profile = get_profile(active_profile_name)

    canonical_errors, canonical_warnings = execute_rules(artifact, CANONICAL_RULES)
    profile_errors, profile_warnings = profile.validate(artifact)
    trust_warnings = _build_trust_warnings(artifact)

    all_errors = canonical_errors + profile_errors
    all_warnings = canonical_warnings + profile_warnings + trust_warnings
    return build_validation_report(
        artifact_id=artifact.artifact_id,
        source_hash=artifact.source.source_hash,
        errors=all_errors,
        warnings=all_warnings,
    )
