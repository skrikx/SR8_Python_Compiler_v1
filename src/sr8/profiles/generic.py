from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule


def _has_objective(artifact: IntentArtifact) -> bool:
    return artifact.objective.strip() != ""


def _has_scope(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.scope)


GENERIC_PROFILE = ProfileDefinition(
    name="generic",
    target_class="generic",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-GEN-001",
            message="generic profile requires objective",
            path="objective",
            severity="error",
            check=_has_objective,
        ),
    ),
    warning_rules=(
        ProfileRule(
            code="VAL-PRO-GEN-002",
            message="generic profile should include scope items",
            path="scope",
            severity="warning",
            check=_has_scope,
        ),
    ),
    supported_transform_targets=("markdown_plan", "markdown_prompt_pack"),
    section_order_hints=("objective", "scope", "constraints", "success_criteria"),
)
