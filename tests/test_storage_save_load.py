from pathlib import Path

from sr8.io.exporters import load_artifact
from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.storage.load import load_by_id, load_canonical, load_derivative
from sr8.storage.save import save_canonical_artifact, save_derivative_artifact
from sr8.storage.workspace import init_workspace


def test_storage_save_and_load_roundtrip(tmp_path: Path) -> None:
    workspace = init_workspace(tmp_path / ".sr8")
    canonical = load_artifact("tests/fixtures/stored_artifact_sample.json")

    canonical_path, _, canonical_record = save_canonical_artifact(workspace, canonical)
    loaded_canonical = load_canonical(canonical_path)
    loaded_by_id = load_by_id(workspace, canonical_record.record_id)

    assert loaded_canonical.artifact_id == canonical.artifact_id
    assert loaded_by_id.artifact_id == canonical.artifact_id

    derivative = DerivativeArtifact.model_validate_json(
        Path("tests/fixtures/stored_derivative_sample.json").read_text(encoding="utf-8")
    )
    derivative_path, _, _, derivative_record = save_derivative_artifact(workspace, derivative)
    loaded_derivative = load_derivative(derivative_path)
    loaded_derivative_by_id = load_by_id(workspace, derivative_record.record_id)

    assert loaded_derivative.derivative_id == derivative.derivative_id
    assert loaded_derivative_by_id.derivative_id == derivative.derivative_id
