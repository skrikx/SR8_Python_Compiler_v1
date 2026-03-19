from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule


def _has_objective(artifact: IntentArtifact) -> bool:
    return artifact.objective.strip() != ""


def _has_output_contract(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.output_contract)


def _has_constraints(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.constraints)


def _has_reusable_structure(artifact: IntentArtifact) -> bool:
    corpus = " ".join([*artifact.scope, *artifact.output_contract, *artifact.constraints]).lower()
    return any(term in corpus for term in ("template", "reuse", "structure", "prompt", "format"))


PROMPT_PACK_PROFILE = ProfileDefinition(
    name="prompt_pack",
    target_class="prompt_pack",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-PRM-001",
            message="prompt_pack profile requires objective",
            path="objective",
            severity="error",
            check=_has_objective,
        ),
        ProfileRule(
            code="VAL-PRO-PRM-002",
            message="prompt_pack profile requires output contract",
            path="output_contract",
            severity="error",
            check=_has_output_contract,
        ),
        ProfileRule(
            code="VAL-PRO-PRM-003",
            message="prompt_pack profile requires constraints",
            path="constraints",
            severity="error",
            check=_has_constraints,
        ),
        ProfileRule(
            code="VAL-PRO-PRM-004",
            message="prompt_pack profile requires reusable structure signal",
            path="scope",
            severity="error",
            check=_has_reusable_structure,
        ),
    ),
    supported_transform_targets=("markdown_prompt_pack",),
    section_order_hints=("objective", "constraints", "scope", "output_contract"),
)
