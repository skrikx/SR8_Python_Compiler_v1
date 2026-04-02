from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from sr8.models.base import SR8Model


class OpenAIProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SR8_OPENAI_", extra="ignore")

    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str | None = None
    timeout_seconds: float = 30.0


class AzureOpenAIProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SR8_AZURE_OPENAI_", extra="ignore")

    api_key: str | None = None
    endpoint: str | None = None
    deployment: str | None = None
    api_version: str = "2024-10-21"
    model: str | None = None
    timeout_seconds: float = 30.0


class AWSBedrockProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SR8_AWS_BEDROCK_", extra="ignore")

    region: str | None = None
    model: str | None = None
    profile: str | None = None
    access_key_id: str | None = None
    secret_access_key: str | None = None
    timeout_seconds: float = 30.0


class AnthropicProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SR8_ANTHROPIC_", extra="ignore")

    api_key: str | None = None
    base_url: str = "https://api.anthropic.com/v1"
    model: str | None = None
    timeout_seconds: float = 30.0


class GeminiProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SR8_GEMINI_", extra="ignore")

    api_key: str | None = None
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    model: str | None = None
    timeout_seconds: float = 30.0


class OllamaProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SR8_OLLAMA_", extra="ignore")

    base_url: str = "http://127.0.0.1:11434"
    model: str | None = None
    timeout_seconds: float = 30.0


ProviderSettings = (
    OpenAIProviderSettings
    | AzureOpenAIProviderSettings
    | AWSBedrockProviderSettings
    | AnthropicProviderSettings
    | GeminiProviderSettings
    | OllamaProviderSettings
)


class ProviderSettingsBundle(SR8Model):
    openai: OpenAIProviderSettings = Field(default_factory=OpenAIProviderSettings)
    azure_openai: AzureOpenAIProviderSettings = Field(default_factory=AzureOpenAIProviderSettings)
    aws_bedrock: AWSBedrockProviderSettings = Field(default_factory=AWSBedrockProviderSettings)
    anthropic: AnthropicProviderSettings = Field(default_factory=AnthropicProviderSettings)
    gemini: GeminiProviderSettings = Field(default_factory=GeminiProviderSettings)
    ollama: OllamaProviderSettings = Field(default_factory=OllamaProviderSettings)

    def for_provider(self, provider: str) -> ProviderSettings:
        mapping: dict[str, ProviderSettings] = {
            "openai": self.openai,
            "azure_openai": self.azure_openai,
            "aws_bedrock": self.aws_bedrock,
            "anthropic": self.anthropic,
            "gemini": self.gemini,
            "ollama": self.ollama,
        }
        try:
            return mapping[provider]
        except KeyError as exc:
            msg = f"Unknown provider settings '{provider}'."
            raise ValueError(msg) from exc


def load_provider_settings() -> ProviderSettingsBundle:
    return ProviderSettingsBundle()
