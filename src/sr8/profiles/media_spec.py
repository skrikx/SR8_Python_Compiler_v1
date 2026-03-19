from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule


def _has_creative_objective(artifact: IntentArtifact) -> bool:
    return artifact.objective.strip() != ""


def _has_output_expectations(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.output_contract)


def _has_constraints(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.constraints)


def _has_style_requirements(artifact: IntentArtifact) -> bool:
    corpus = " ".join([*artifact.constraints, *artifact.scope, *artifact.assumptions]).lower()
    return any(term in corpus for term in ("style", "tone", "format", "structure", "visual"))


MEDIA_SPEC_PROFILE = ProfileDefinition(
    name="media_spec",
    target_class="media_spec",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-MED-001",
            message="media_spec profile requires creative objective",
            path="objective",
            severity="error",
            check=_has_creative_objective,
        ),
        ProfileRule(
            code="VAL-PRO-MED-002",
            message="media_spec profile requires output expectations",
            path="output_contract",
            severity="error",
            check=_has_output_expectations,
        ),
        ProfileRule(
            code="VAL-PRO-MED-003",
            message="media_spec profile requires constraints",
            path="constraints",
            severity="error",
            check=_has_constraints,
        ),
        ProfileRule(
            code="VAL-PRO-MED-004",
            message="media_spec profile requires style or structure requirements",
            path="scope",
            severity="error",
            check=_has_style_requirements,
        ),
    ),
    supported_transform_targets=("markdown_prompt_pack",),
    section_order_hints=("objective", "scope", "constraints", "output_contract"),
)
