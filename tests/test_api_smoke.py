import json
from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app


def test_api_health_compile_validate_transform(tmp_path: Path) -> None:
    client = TestClient(app)
    source_text = Path("examples/product_prd.md").read_text(encoding="utf-8")

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    compile_response = client.post(
        "/compile",
        json={"source_text": source_text, "profile": "prd"},
    )
    assert compile_response.status_code == 200
    assert compile_response.json()["receipt"]["compile_kind"] in {
        "semantic_compile",
        "canonicalize_structured",
    }
    artifact_payload = compile_response.json()["artifact"]

    artifact_path = tmp_path / "artifact.json"
    artifact_path.write_text(json.dumps(artifact_payload), encoding="utf-8")

    validate_response = client.post(
        "/validate",
        json={"artifact_path": str(artifact_path)},
    )
    assert validate_response.status_code == 200
    assert validate_response.json()["payload"]["readiness_status"] in {"pass", "warn", "fail"}

    inspect_response = client.post("/inspect", json={"target": str(artifact_path)})
    assert inspect_response.status_code == 200
    assert inspect_response.json()["mode"] == "artifact"
    assert inspect_response.json()["artifact"]["artifact_id"] == artifact_payload["artifact_id"]

    transform_response = client.post(
        "/transform",
        json={"artifact_path": str(artifact_path), "target": "markdown_prd"},
    )
    assert transform_response.status_code == 200
    assert transform_response.json()["payload"]["transform_target"] == "markdown_prd"
