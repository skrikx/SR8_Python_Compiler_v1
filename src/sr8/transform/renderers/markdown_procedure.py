from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact


def _bullet_section(title: str, items: list[str]) -> str:
    if not items:
        return f"## {title}\n- (none)\n"
    rows = "\n".join(f"- {item}" for item in items)
    return f"## {title}\n{rows}\n"


def render_markdown_procedure(artifact: IntentArtifact) -> str:
    fallback_items = [
        item
        for item in artifact.constraints
        if "fallback" in item.lower() or "rollback" in item.lower()
    ] or artifact.constraints
    escalation_items = [
        item
        for item in [*artifact.constraints, *artifact.success_criteria]
        if any(term in item.lower() for term in ("escalat", "review", "approval", "owner"))
    ] or artifact.success_criteria
    parts = [
        f"# Procedure - {artifact.artifact_id}",
        "## Purpose",
        artifact.objective or "(empty)",
        "## Authority Context",
        artifact.authority_context or "(empty)",
        _bullet_section("Steps", artifact.scope),
        _bullet_section("Fallbacks", fallback_items),
        _bullet_section("Escalation", escalation_items),
    ]
    return "\n".join(parts).strip() + "\n"
