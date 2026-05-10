from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule


def _has_authority_context(artifact: IntentArtifact) -> bool:
    return artifact.authority_context.strip() != ""


def _has_stepwise_structure(artifact: IntentArtifact) -> bool:
    return any(
        item.strip().lower().startswith(("step", "1.", "2.", "3.", "phase"))
        for item in artifact.scope
    )


def _has_fallback_conditions(artifact: IntentArtifact) -> bool:
    corpus = " ".join([*artifact.constraints, *artifact.assumptions]).lower()
    return any(term in corpus for term in ("fallback", "if fail", "retry", "rollback"))


def _has_escalation_conditions(artifact: IntentArtifact) -> bool:
    corpus = " ".join([*artifact.constraints, *artifact.success_criteria]).lower()
    return any(term in corpus for term in ("escalat", "review", "approval", "owner"))


PROCEDURE_PROFILE = ProfileDefinition(
    name="procedure",
    target_class="procedure",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-PRC-001",
            message="procedure profile requires authority context",
            path="authority_context",
            severity="error",
            check=_has_authority_context,
        ),
        ProfileRule(
            code="VAL-PRO-PRC-002",
            message="procedure profile requires stepwise operational structure",
            path="scope",
            severity="error",
            check=_has_stepwise_structure,
        ),
        ProfileRule(
            code="VAL-PRO-PRC-003",
            message="procedure profile requires fallback conditions",
            path="constraints",
            severity="error",
            check=_has_fallback_conditions,
        ),
        ProfileRule(
            code="VAL-PRO-PRC-004",
            message="procedure profile requires escalation or review conditions",
            path="success_criteria",
            severity="error",
            check=_has_escalation_conditions,
        ),
    ),
    supported_transform_targets=(
        "markdown_procedure",
        "markdown_plan",
        "xml_promptunit_package",
        "xml_sr8_prompt",
        "xml_safe_alternative_package",
        "xml_srxml_rc2",
    ),
    section_order_hints=("objective", "authority_context", "scope", "constraints"),
)
