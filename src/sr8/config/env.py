from __future__ import annotations

from pydantic_settings import SettingsConfigDict

ENV_FILES: tuple[str, str] = (".env", ".env.local")


def settings_config(*, env_prefix: str) -> SettingsConfigDict:
    return SettingsConfigDict(
        env_prefix=env_prefix,
        env_file=ENV_FILES,
        env_file_encoding="utf-8",
        extra="ignore",
    )
