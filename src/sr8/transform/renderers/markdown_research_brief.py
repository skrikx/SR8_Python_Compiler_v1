from __future__ import annotations

from sr8.models.intent_artifact import IntentArtifact


def _bullet_section(title: str, items: list[str]) -> str:
    if not items:
        return f"## {title}\n- (none)\n"
    rows = "\n".join(f"- {item}" for item in items)
    return f"## {title}\n{rows}\n"


def render_markdown_research_brief(artifact: IntentArtifact) -> str:
    parts = [
        f"# Research Brief - {artifact.artifact_id}",
        "## Research Objective",
        artifact.objective or "(empty)",
        "## Question",
        artifact.objective or "(empty)",
        _bullet_section("Constraints", artifact.constraints),
        _bullet_section("Evidence Expectations", artifact.success_criteria),
        _bullet_section("Output Structure", artifact.output_contract),
    ]
    return "\n".join(parts).strip() + "\n"
