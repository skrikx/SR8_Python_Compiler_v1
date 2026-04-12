from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app


def test_frontend_api_contracts(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(app)

    status_response = client.get("/status")
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["status"] == "ok"
    assert "providers" in status_payload

    providers_response = client.get("/providers")
    assert providers_response.status_code == 200
    assert any(item["name"] == "openai" for item in providers_response.json()["providers"])

    probe_response = client.get("/providers/probe")
    assert probe_response.status_code == 200
    assert "results" in probe_response.json()

    settings_response = client.get("/settings")
    assert settings_response.status_code == 200
    assert "workspace_path" in settings_response.json()["settings"]

    artifacts_response = client.get("/artifacts")
    assert artifacts_response.status_code == 200
    assert artifacts_response.json()["records"] == []

    receipts_response = client.get("/receipts")
    assert receipts_response.status_code == 200
    assert receipts_response.json()["receipts"] == []

    compile_response = client.post(
        "/compile",
        json={
            "source": "Objective: Frontend contract\nScope:\n- one\n",
            "profile": "generic",
            "rule_only": True,
        },
    )
    assert compile_response.status_code == 200
    assert compile_response.json()["artifact"]["objective"] == "Frontend contract"
    assert compile_response.json()["receipt"]["compile_kind"] == "semantic_compile"
