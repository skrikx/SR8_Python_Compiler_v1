from __future__ import annotations

from typing import TYPE_CHECKING

from sr8.config.provider_settings import load_provider_settings

if TYPE_CHECKING:
    from sr8.adapters.base import ProviderAdapter


def create_provider(name: str) -> ProviderAdapter:
    key = name.strip().lower()
    settings = load_provider_settings()
    if key == "openai":
        from sr8.adapters.openai_adapter import OpenAIAdapter

        return OpenAIAdapter(settings.openai)
    if key == "azure_openai":
        from sr8.adapters.azure_openai_adapter import AzureOpenAIAdapter

        return AzureOpenAIAdapter(settings.azure_openai)
    if key == "aws_bedrock":
        from sr8.adapters.bedrock_adapter import BedrockAdapter

        return BedrockAdapter(settings.aws_bedrock)
    if key == "anthropic":
        from sr8.adapters.anthropic_adapter import AnthropicAdapter

        return AnthropicAdapter(settings.anthropic)
    if key == "gemini":
        from sr8.adapters.gemini_adapter import GeminiAdapter

        return GeminiAdapter(settings.gemini)
    if key == "ollama":
        from sr8.adapters.ollama_adapter import OllamaAdapter

        return OllamaAdapter(settings.ollama)
    msg = f"Unknown provider '{name}'."
    raise ValueError(msg)
