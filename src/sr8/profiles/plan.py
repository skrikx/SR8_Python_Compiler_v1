from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule


def _has_objective(artifact: IntentArtifact) -> bool:
    return artifact.objective.strip() != ""


def _has_ordered_work(artifact: IntentArtifact) -> bool:
    return any(
        item.strip().lower().startswith(("phase", "step", "milestone", "1.", "2."))
        for item in artifact.scope
    )


def _has_dependencies(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.dependencies)


def _has_success_criteria(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.success_criteria)


PLAN_PROFILE = ProfileDefinition(
    name="plan",
    target_class="plan",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-PLN-001",
            message="plan profile requires objective",
            path="objective",
            severity="error",
            check=_has_objective,
        ),
        ProfileRule(
            code="VAL-PRO-PLN-002",
            message="plan profile requires phased or ordered scope",
            path="scope",
            severity="error",
            check=_has_ordered_work,
        ),
        ProfileRule(
            code="VAL-PRO-PLN-003",
            message="plan profile requires dependencies",
            path="dependencies",
            severity="error",
            check=_has_dependencies,
        ),
        ProfileRule(
            code="VAL-PRO-PLN-004",
            message="plan profile requires success criteria",
            path="success_criteria",
            severity="error",
            check=_has_success_criteria,
        ),
    ),
    supported_transform_targets=(
        "markdown_plan",
        "markdown_prompt_pack",
        "xml_promptunit_package",
        "xml_sr8_prompt",
        "xml_safe_alternative_package",
        "xml_srxml_rc2",
    ),
    section_order_hints=("objective", "scope", "dependencies", "success_criteria"),
)
