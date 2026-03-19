from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.base import ProfileDefinition, ProfileRule


def _has_research_objective(artifact: IntentArtifact) -> bool:
    return artifact.objective.strip() != ""


def _has_evidence_expectations(artifact: IntentArtifact) -> bool:
    corpus = " ".join([*artifact.success_criteria, *artifact.output_contract]).lower()
    return any(term in corpus for term in ("evidence", "sources", "citations", "findings"))


def _has_method_bounds(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.constraints)


def _has_report_structure(artifact: IntentArtifact) -> bool:
    return any(item.strip() for item in artifact.output_contract)


RESEARCH_BRIEF_PROFILE = ProfileDefinition(
    name="research_brief",
    target_class="research_brief",
    required_rules=(
        ProfileRule(
            code="VAL-PRO-RSH-001",
            message="research_brief profile requires objective or research question",
            path="objective",
            severity="error",
            check=_has_research_objective,
        ),
        ProfileRule(
            code="VAL-PRO-RSH-002",
            message="research_brief profile requires evidence expectations",
            path="success_criteria",
            severity="error",
            check=_has_evidence_expectations,
        ),
        ProfileRule(
            code="VAL-PRO-RSH-003",
            message="research_brief profile requires method constraints",
            path="constraints",
            severity="error",
            check=_has_method_bounds,
        ),
        ProfileRule(
            code="VAL-PRO-RSH-004",
            message="research_brief profile requires output structure",
            path="output_contract",
            severity="error",
            check=_has_report_structure,
        ),
    ),
    supported_transform_targets=("markdown_research_brief", "markdown_plan"),
    section_order_hints=("objective", "constraints", "success_criteria", "output_contract"),
)
