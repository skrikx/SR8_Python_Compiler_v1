from __future__ import annotations

from pathlib import Path

from sr8.config.provider_settings import OpenAIProviderSettings
from sr8.config.settings import SR8Settings


def test_sr8_settings_load_from_dotenv(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SR8_DEFAULT_PROFILE", raising=False)
    (tmp_path / ".env").write_text("SR8_DEFAULT_PROFILE=plan\n", encoding="utf-8")

    settings = SR8Settings()

    assert settings.default_profile == "plan"


def test_provider_settings_load_from_dotenv(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SR8_OPENAI_MODEL", raising=False)
    env_text = "SR8_OPENAI_API_KEY=test-key\nSR8_OPENAI_MODEL=gpt-test\n"
    (tmp_path / ".env").write_text(env_text, encoding="utf-8")

    settings = OpenAIProviderSettings()

    assert settings.api_key == "test-key"
    assert settings.model == "gpt-test"


def test_environment_variables_override_dotenv(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text("SR8_OPENAI_MODEL=gpt-dotenv\n", encoding="utf-8")
    monkeypatch.setenv("SR8_OPENAI_MODEL", "gpt-env")

    settings = OpenAIProviderSettings()

    assert settings.model == "gpt-env"
