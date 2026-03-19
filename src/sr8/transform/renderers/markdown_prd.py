from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact


def _bullet_section(title: str, items: list[str]) -> str:
    if not items:
        return f"## {title}\n- (none)\n"
    rows = "\n".join(f"- {item}" for item in items)
    return f"## {title}\n{rows}\n"


def render_markdown_prd(artifact: IntentArtifact) -> str:
    parts = [
        f"# PRD - {artifact.artifact_id}",
        "## Summary",
        f"Profile: {artifact.profile}",
        "## Problem",
        artifact.objective or "(empty)",
        "## Objective",
        artifact.objective or "(empty)",
        _bullet_section("Scope", artifact.scope),
        _bullet_section("Non-goals", artifact.exclusions),
        _bullet_section("Constraints", artifact.constraints),
        _bullet_section("Success Criteria", artifact.success_criteria),
    ]
    return "\n".join(parts).strip() + "\n"
