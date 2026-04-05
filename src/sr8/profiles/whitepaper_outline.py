from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule


def _has_objective(artifact: IntentArtifact) -> bool:
    return artifact.objective.strip() != ""


def _has_sections(artifact: IntentArtifact) -> bool:
    return bool(artifact.scope or artifact.output_contract or artifact.success_criteria)


WHITEPAPER_OUTLINE_PROFILE = ProfileDefinition(
    name="whitepaper_outline",
    target_class="whitepaper_outline",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-WPO-001",
            message="whitepaper_outline requires objective",
            path="objective",
            severity="error",
            check=_has_objective,
        ),
        ProfileRule(
            code="VAL-PRO-WPO-002",
            message="whitepaper_outline requires outline sections",
            path="scope",
            severity="error",
            check=_has_sections,
        ),
    ),
    supported_transform_targets=(
        "markdown_plan",
        "markdown_prompt_pack",
        "xml_promptunit_package",
        "xml_sr8_prompt",
        "xml_safe_alternative_package",
    ),
)
