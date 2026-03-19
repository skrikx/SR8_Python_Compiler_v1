from sr8.io.exporters import load_artifact
from sr8.transform.engine import transform_artifact


def test_markdown_prd_sections_present() -> None:
    artifact = load_artifact("tests/fixtures/compiled_prd_artifact.json")
    content = transform_artifact(artifact, target="markdown_prd").derivative.content
    assert "## Summary" in content
    assert "## Problem" in content
    assert "## Objective" in content
    assert "## Scope" in content
    assert "## Non-goals" in content
    assert "## Constraints" in content
    assert "## Success Criteria" in content


def test_markdown_plan_sections_present() -> None:
    artifact = load_artifact("tests/fixtures/compiled_plan_artifact.json")
    content = transform_artifact(artifact, target="markdown_plan").derivative.content
    assert "## Goal" in content
    assert "## Scope" in content
    assert "## Dependencies" in content
    assert "## Phases" in content
    assert "## Success Criteria" in content


def test_markdown_research_sections_present() -> None:
    artifact = load_artifact("tests/fixtures/compiled_research_artifact.json")
    content = transform_artifact(artifact, target="markdown_research_brief").derivative.content
    assert "## Research Objective" in content
    assert "## Question" in content
    assert "## Constraints" in content
    assert "## Evidence Expectations" in content
    assert "## Output Structure" in content
