from pathlib import Path

import pytest

from sr8.io.exporters import load_artifact
from sr8.transform.engine import transform_artifact, write_derivative


def test_transform_engine_produces_derivative_with_lineage() -> None:
    artifact = load_artifact("tests/fixtures/compiled_prd_artifact.json")
    result = transform_artifact(artifact, target="markdown_prd")

    derivative = result.derivative
    assert derivative.parent_artifact_id == artifact.artifact_id
    assert derivative.transform_target == "markdown_prd"
    assert derivative.lineage.parent_source_hash == artifact.source.source_hash
    assert "renderer_version" in derivative.metadata


def test_transform_incompatible_target_fails() -> None:
    artifact = load_artifact("tests/fixtures/compiled_prd_artifact.json")
    with pytest.raises(ValueError):
        transform_artifact(artifact, target="markdown_research_brief")


def test_transform_write_behavior(tmp_path: Path) -> None:
    artifact = load_artifact("tests/fixtures/compiled_plan_artifact.json")
    derivative = transform_artifact(artifact, target="markdown_plan").derivative
    derivative_path, latest_path = write_derivative(derivative, out_dir=tmp_path)
    assert derivative_path.exists()
    assert latest_path.exists()
