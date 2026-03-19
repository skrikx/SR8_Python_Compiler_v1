from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact


def _bullet_section(title: str, items: list[str]) -> str:
    if not items:
        return f"## {title}\n- (none)\n"
    rows = "\n".join(f"- {item}" for item in items)
    return f"## {title}\n{rows}\n"


def render_markdown_prompt_pack(artifact: IntentArtifact) -> str:
    structure = artifact.scope or ["System context", "Task", "Constraints", "Output schema"]
    parts = [
        f"# Prompt Pack - {artifact.artifact_id}",
        "## Objective",
        artifact.objective or "(empty)",
        _bullet_section("Constraints", artifact.constraints),
        _bullet_section("Reusable Prompt Structure", structure),
        _bullet_section("Output Contract", artifact.output_contract),
    ]
    return "\n".join(parts).strip() + "\n"
