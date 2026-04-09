import json
from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app
from sr8.compiler import compile_intent


def test_workspace_override_is_denied_by_default(tmp_path: Path, monkeypatch) -> None:
    default_workspace = tmp_path / "default" / ".sr8"
    other_workspace = tmp_path / "other" / ".sr8"
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(default_workspace))
    client = TestClient(app)

    response = client.post(
        "/lint",
        json={"artifact_ref": "art_missing", "workspace_path": str(other_workspace)},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "workspace_access_denied"


def test_inspect_allows_configured_workspace_only(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / "configured" / ".sr8"
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(workspace))
    client = TestClient(app)
    artifact = compile_intent("Objective: Isolated\nScope:\n- one\n").artifact
    artifact_path = tmp_path / "artifact.json"
    artifact_path.write_text(json.dumps(artifact.model_dump(mode="json")), encoding="utf-8")

    response = client.post(
        "/inspect",
        json={"target": str(artifact_path), "workspace_path": str(workspace)},
    )

    assert response.status_code == 200
    assert response.json()["route_contract"]["exposure_class"] == "trusted-local"
