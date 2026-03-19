from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact


def _bullet_section(title: str, items: list[str]) -> str:
    if not items:
        return f"## {title}\n- (none)\n"
    rows = "\n".join(f"- {item}" for item in items)
    return f"## {title}\n{rows}\n"


def render_markdown_plan(artifact: IntentArtifact) -> str:
    scope_items = artifact.scope
    phase_items = [
        item
        for item in scope_items
        if item.lower().startswith(("phase", "step", "milestone", "1.", "2."))
    ] or scope_items
    parts = [
        f"# Plan - {artifact.artifact_id}",
        "## Goal",
        artifact.objective or "(empty)",
        _bullet_section("Scope", scope_items),
        _bullet_section("Dependencies", artifact.dependencies),
        _bullet_section("Phases", phase_items),
        _bullet_section("Success Criteria", artifact.success_criteria),
    ]
    return "\n".join(parts).strip() + "\n"
