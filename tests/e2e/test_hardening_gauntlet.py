from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app
from sr8.compiler import CompileConfig, compile_intent
from sr8.storage.save import save_canonical_artifact
from sr8.storage.workspace import init_workspace


def test_compile_to_transform_and_diff_gauntlet(tmp_path: Path, monkeypatch) -> None:
    workspace_root = tmp_path / ".sr8"
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(workspace_root))
    workspace = init_workspace(workspace_root)
    primary_source = (
        "Objective: Ship the operator console\n"
        "Scope:\n"
        "- show trust\n"
        "Success Criteria:\n"
        "- operator can inspect outputs\n"
    )
    secondary_source = (
        "Objective: Ship the operator console safely\n"
        "Scope:\n"
        "- show trust\n"
        "- preserve replay\n"
        "Success Criteria:\n"
        "- operator can inspect outputs\n"
    )

    primary = compile_intent(
        primary_source,
        config=CompileConfig(profile="generic"),
    )
    secondary = compile_intent(
        secondary_source,
        config=CompileConfig(profile="generic"),
    )

    primary_path, _, primary_record = save_canonical_artifact(workspace, primary.artifact)
    _, _, secondary_record = save_canonical_artifact(workspace, secondary.artifact)

    client = TestClient(app)

    inspect_response = client.post(
        "/inspect",
        json={"target": primary_record.artifact_id, "workspace_path": str(workspace_root)},
    )
    assert inspect_response.status_code == 200
    assert inspect_response.json()["artifact"]["artifact_id"] == primary_record.artifact_id

    validate_response = client.post("/validate", json={"artifact_path": str(primary_path)})
    assert validate_response.status_code == 200
    assert validate_response.json()["payload"]["readiness_status"] in {"pass", "warn", "fail"}

    transform_response = client.post(
        "/transform",
        json={"artifact_path": str(primary_path), "target": "markdown_plan"},
    )
    assert transform_response.status_code == 200
    assert transform_response.json()["payload"]["parent_artifact_id"] == primary_record.artifact_id

    lint_response = client.post(
        "/lint",
        json={"artifact_ref": primary_record.artifact_id, "workspace_path": str(workspace_root)},
    )
    assert lint_response.status_code == 200
    assert "payload" in lint_response.json()

    diff_response = client.post(
        "/diff",
        json={
            "left": primary_record.artifact_id,
            "right": secondary_record.artifact_id,
            "workspace_path": str(workspace_root),
        },
    )
    assert diff_response.status_code == 200
    diff_payload = diff_response.json()["payload"]
    assert diff_payload["changes"]
    assert any(change["field"] == "objective" for change in diff_payload["changes"])
