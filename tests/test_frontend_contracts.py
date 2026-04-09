from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app


def test_frontend_relied_on_provider_and_compile_metadata(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(app)

    providers_response = client.get("/providers")
    assert providers_response.status_code == 200
    provider = providers_response.json()["providers"][0]
    assert provider["runtime_transport"] in {"http", "sdk"}
    assert "default_model_env_var" in provider

    compile_response = client.post(
        "/compile",
        json={
            "source": "Objective: Frontend trust\nScope:\n- one\n",
            "profile": "generic",
            "rule_only": True,
        },
    )
    assert compile_response.status_code == 200
    payload = compile_response.json()
    assert payload["route_contract"]["route_id"] == "compile"
    assert payload["request_identity"]["auth_mode"] in {"trusted-local", "bearer-token"}
    assert "weak_intent_recovery" in payload["artifact"]["metadata"]


def test_frontend_async_compile_contract_is_pollable(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(app)

    response = client.post(
        "/compile",
        json={
            "source": "Objective: Frontend async\nScope:\n- one\n",
            "rule_only": True,
            "async_mode": True,
            "idempotency_key": "frontend-async",
        },
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["route_contract"]["route_id"] == "compile"
    assert payload["job"]["job_id"].startswith("job_")


def test_frontend_types_track_route_contracts() -> None:
    content = Path("frontend/src/lib/api/types.ts").read_text(encoding="utf-8")

    assert "export interface RouteContract" in content
    assert "export interface CompileResponse" in content
    assert "route_contract: RouteContract;" in content
    assert "request_identity: RequestIdentity;" in content
