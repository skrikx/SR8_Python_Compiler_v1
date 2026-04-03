from __future__ import annotations

from sr8.frontdoor.package_models import GovernanceDecision
from sr8.models.intent_artifact import IntentArtifact


def evaluate_governance(artifact: IntentArtifact) -> GovernanceDecision:
    flags = artifact.governance_flags
    if flags.requires_human_review:
        return GovernanceDecision(
            status="safe_alternative_compile",
            reason="requires_human_review",
            notes=["Human review required before release."],
        )
    if flags.ambiguous or flags.incomplete:
        notes = []
        if flags.ambiguous:
            notes.append("Intent ambiguity detected.")
        if flags.incomplete:
            notes.append("Intent incomplete or underspecified.")
        return GovernanceDecision(
            status="safe_alternative_compile",
            reason="ambiguous_or_incomplete",
            notes=notes,
        )
    return GovernanceDecision(status="allow", reason="clear")


def suggest_safe_alternative(artifact: IntentArtifact) -> str:
    objective = artifact.objective.strip() or "your request"
    return (
        "Provide a safe, high-level brief and a set of clarifying questions to "
        f"complete {objective}."
    )
