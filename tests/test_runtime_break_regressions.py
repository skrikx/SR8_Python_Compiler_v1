import json
from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app
from sr8.compiler import CompileConfig, compile_intent
from sr8.storage.save import save_canonical_artifact, save_derivative_artifact
from sr8.storage.workspace import init_workspace
from sr8.transform.engine import transform_artifact


def test_runtime_break_regressions_close_together(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(app)

    local_source = tmp_path / "break.txt"
    local_source.write_text("should stay unread", encoding="utf-8")

    rejected = client.post("/compile", json={"source": str(local_source)})
    assert rejected.status_code == 422
    assert rejected.json()["error"]["code"] == "path_input_disallowed"

    inspect_rejected = client.post("/inspect", json={"target": "Objective: Runtime regression"})
    assert inspect_rejected.status_code == 422
    assert inspect_rejected.json()["error"]["code"] == "inspect_target_must_be_artifact"

    compiled = compile_intent(
        "Objective: Runtime regression\nScope:\n- one\n",
        config=CompileConfig(profile="prd", extraction_adapter="rule_based"),
    )
    workspace = init_workspace(tmp_path / ".sr8")
    artifact_path, _, _ = save_canonical_artifact(workspace, compiled.artifact)

    validate_response = client.post("/validate", json={"artifact_path": str(artifact_path)})
    assert validate_response.status_code == 200

    transformed = transform_artifact(compiled.artifact, "markdown_prd")
    _, _, _, derivative_record = save_derivative_artifact(workspace, transformed.derivative)
    assert derivative_record.target_class is None

    probe_response = client.get("/providers/probe", params={"provider": "aws_bedrock"})
    assert probe_response.status_code == 200
    probe_payload = probe_response.json()
    assert probe_payload["ready_for_runtime"] is False
    assert probe_payload["available"] is False

    catalog_payload = json.loads(workspace.catalog_path.read_text(encoding="utf-8"))
    assert len(catalog_payload["records"]) == 2
