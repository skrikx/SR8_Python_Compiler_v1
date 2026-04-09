from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app


def test_compile_rejects_path_looking_input_without_leaking_content(tmp_path: Path) -> None:
    secret_path = tmp_path / "secret.txt"
    secret_path.write_text("TOP SECRET CONTENT", encoding="utf-8")
    client = TestClient(app)

    response = client.post("/compile", json={"source": str(secret_path), "profile": "generic"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "path_input_disallowed"
    assert "TOP SECRET CONTENT" not in response.text


def test_compile_rejects_conflicting_source_forms() -> None:
    client = TestClient(app)

    response = client.post(
        "/compile",
        json={
            "source": "Objective: conflict\n",
            "source_payload": {"objective": "Structured conflict"},
            "profile": "generic",
        },
    )

    assert response.status_code == 422


def test_provider_outage_falls_back_to_rule_based(monkeypatch) -> None:
    client = TestClient(app)

    def raise_error(name: str):
        from sr8.adapters.errors import ProviderExecutionError

        raise ProviderExecutionError(name, "provider unavailable")

    monkeypatch.setattr("sr8.compiler.model_assist.create_provider", raise_error)

    response = client.post(
        "/compile",
        json={
            "source": "Objective: Chaos fallback\nScope:\n- one\n",
            "profile": "generic",
            "assist_provider": "openai",
            "assist_model": "gpt-test",
        },
    )

    assert response.status_code == 200
    provider_assist = response.json()["artifact"]["metadata"]["provider_assist"]
    assert provider_assist["assist_extract_status"] == "fallback_rule_based"
    assert provider_assist["fallback"] == "rule_based"

