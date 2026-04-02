from sr8.adapters.factory import create_provider


def test_openai_probe_reports_missing_env(monkeypatch) -> None:
    monkeypatch.delenv("SR8_OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("SR8_OPENAI_MODEL", raising=False)

    result = create_provider("openai").probe()

    assert result.provider == "openai"
    assert result.configured is False
    assert "SR8_OPENAI_API_KEY" in result.missing_env_vars
    assert "SR8_OPENAI_MODEL" in result.missing_env_vars


def test_ollama_probe_uses_local_availability(monkeypatch) -> None:
    monkeypatch.setenv("SR8_OLLAMA_MODEL", "llama3.1")

    result = create_provider("ollama").probe()

    assert result.provider == "ollama"
    assert result.available is True
    assert result.configured is True
