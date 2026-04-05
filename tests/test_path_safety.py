from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from sr8.api.app import app
from sr8.utils.paths import resolve_trusted_local_path


def test_resolve_trusted_local_path_accepts_repo_relative_fixture() -> None:
    path = resolve_trusted_local_path("tests/fixtures/compiled_prd_artifact.json", must_exist=True)

    assert path.name == "compiled_prd_artifact.json"
    assert path.exists()


def test_resolve_trusted_local_path_accepts_temp_path(tmp_path: Path) -> None:
    artifact_path = tmp_path / "artifact.json"
    artifact_path.write_text("{}", encoding="utf-8")

    resolved = resolve_trusted_local_path(artifact_path, must_exist=True)

    assert resolved == artifact_path.resolve()


def test_resolve_trusted_local_path_rejects_outside_trusted_roots() -> None:
    outside_root = Path.home().resolve().parent / "sr8-outside-root" / "artifact.json"

    with pytest.raises(ValueError, match="trusted local roots"):
        resolve_trusted_local_path(outside_root)


def test_api_validate_rejects_outside_trusted_local_roots() -> None:
    client = TestClient(app)
    outside_root = Path.home().resolve().parent / "sr8-outside-root" / "artifact.json"

    response = client.post("/validate", json={"artifact_path": str(outside_root)})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_artifact_reference"
