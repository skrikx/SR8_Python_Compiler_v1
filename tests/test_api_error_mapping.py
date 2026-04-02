from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app


def test_api_compile_invalid_provider_maps_to_422() -> None:
    client = TestClient(app)

    response = client.post(
        "/compile",
        json={
            "source": "Objective: Invalid provider\nScope:\n- one\n",
            "assist_provider": "bogus",
            "assist_model": "bogus-model",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_provider"


def test_api_missing_artifact_maps_to_404(tmp_path: Path) -> None:
    client = TestClient(app)
    missing_path = tmp_path / "missing.json"

    response = client.post("/validate", json={"artifact_path": str(missing_path)})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "artifact_not_found"


def test_api_invalid_artifact_json_maps_to_422(tmp_path: Path) -> None:
    client = TestClient(app)
    invalid_path = tmp_path / "artifact.json"
    invalid_path.write_text("{not-json", encoding="utf-8")

    response = client.post("/validate", json={"artifact_path": str(invalid_path)})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_artifact_payload"


def test_api_binary_artifact_maps_to_415(tmp_path: Path) -> None:
    client = TestClient(app)
    binary_path = tmp_path / "artifact.json"
    binary_path.write_bytes(b"\xff\xfe\x00\x01")

    response = client.post("/validate", json={"artifact_path": str(binary_path)})

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_artifact_content"
