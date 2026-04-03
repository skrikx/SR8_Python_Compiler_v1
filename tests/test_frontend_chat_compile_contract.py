from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app


def test_frontend_chat_compile_contract(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(app)
    response = client.post(
        "/compile",
        json={
            "source": "compile: Objective: Draft a launch brief\nScope:\n- Step one",
            "profile": "generic",
            "rule_only": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["frontdoor"]["entry_mode"] == "chat_compile"
    assert "promptunit_package_xml" in payload["frontdoor"]
