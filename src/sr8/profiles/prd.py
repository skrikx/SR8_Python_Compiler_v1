from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule

STAKEHOLDER_TERMS = ("user", "customer", "stakeholder", "buyer")


def _has_problem_framing(artifact: IntentArtifact) -> bool:
    return artifact.objective.strip() != ""


def _has_stakeholder_signal(artifact: IntentArtifact) -> bool:
    corpus = " ".join(
        [artifact.objective, *artifact.scope, *artifact.assumptions, artifact.authority_context]
    ).lower()
    return any(term in corpus for term in STAKEHOLDER_TERMS)


def _has_functional_scope(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.scope)


def _has_non_goals(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.exclusions)


def _has_success_metrics(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.success_criteria)


PRD_PROFILE = ProfileDefinition(
    name="prd",
    target_class="prd",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-PRD-001",
            message="prd profile requires objective/problem statement",
            path="objective",
            severity="error",
            check=_has_problem_framing,
        ),
        ProfileRule(
            code="VAL-PRO-PRD-002",
            message="prd profile requires user or stakeholder signal",
            path="objective",
            severity="error",
            check=_has_stakeholder_signal,
        ),
        ProfileRule(
            code="VAL-PRO-PRD-003",
            message="prd profile requires functional scope",
            path="scope",
            severity="error",
            check=_has_functional_scope,
        ),
        ProfileRule(
            code="VAL-PRO-PRD-004",
            message="prd profile requires exclusions/non-goals",
            path="exclusions",
            severity="error",
            check=_has_non_goals,
        ),
        ProfileRule(
            code="VAL-PRO-PRD-005",
            message="prd profile requires success criteria or metrics",
            path="success_criteria",
            severity="error",
            check=_has_success_metrics,
        ),
    ),
    supported_transform_targets=(
        "markdown_prd",
        "markdown_plan",
        "markdown_prompt_pack",
        "xml_promptunit_package",
        "xml_sr8_prompt",
        "xml_safe_alternative_package",
    ),
    section_order_hints=(
        "objective",
        "scope",
        "exclusions",
        "constraints",
        "success_criteria",
    ),
)
