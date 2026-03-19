from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.models.validation import ValidationReport
from sr8.profiles.registry import get_profile
from sr8.validate.report import build_validation_report
from sr8.validate.rules import CANONICAL_RULES, execute_rules


def validate_artifact(
    artifact: IntentArtifact,
    profile_name: str | None = None,
) -> ValidationReport:
    active_profile_name = profile_name or artifact.profile or "generic"
    profile = get_profile(active_profile_name)

    canonical_errors, canonical_warnings = execute_rules(artifact, CANONICAL_RULES)
    profile_errors, profile_warnings = profile.validate(artifact)

    all_errors = canonical_errors + profile_errors
    all_warnings = canonical_warnings + profile_warnings
    return build_validation_report(
        artifact_id=artifact.artifact_id,
        source_hash=artifact.source.source_hash,
        errors=all_errors,
        warnings=all_warnings,
    )
