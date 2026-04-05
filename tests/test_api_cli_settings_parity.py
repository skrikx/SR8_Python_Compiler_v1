from fastapi.testclient import TestClient

from sr8.api.app import app
from sr8.config.settings import SR8Settings, resolve_compile_config


def test_api_settings_and_compile_share_runtime_resolution(monkeypatch) -> None:
    monkeypatch.setenv("SR8_DEFAULT_PROFILE", "prd")
    monkeypatch.setenv("SR8_INCLUDE_RAW_SOURCE", "true")
    monkeypatch.setenv("SR8_ASSIST_PROVIDER", "openai")
    monkeypatch.setenv("SR8_ASSIST_MODEL", "gpt-test")

    client = TestClient(app)
    settings = SR8Settings()
    resolved = resolve_compile_config(settings)

    settings_response = client.get("/settings")
    compile_response = client.post(
        "/compile",
        json={"source": "Objective: Settings parity\nScope:\n- one\n"},
    )

    assert settings_response.status_code == 200
    assert compile_response.status_code == 200

    payload = settings_response.json()
    artifact = compile_response.json()["artifact"]
    trace = artifact["metadata"]["extraction_trace"]

    assert payload["default_profile"] == resolved.profile
    assert payload["extraction_adapter"] == resolved.extraction_adapter
    assert payload["assist_provider"] == resolved.assist_provider
    assert payload["assist_model"] == resolved.assist_model
    assert payload["include_raw_source"] == resolved.include_raw_source
    assert artifact["profile"] == resolved.profile
    assert artifact["metadata"]["raw_content"].startswith("Objective: Settings parity")
    assert trace["metadata"]["provider"] == resolved.assist_provider

