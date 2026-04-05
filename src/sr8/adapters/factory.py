from __future__ import annotations

from sr8.adapters.anthropic_adapter import AnthropicAdapter
from sr8.adapters.azure_openai_adapter import AzureOpenAIAdapter
from sr8.adapters.base import ProviderAdapter
from sr8.adapters.bedrock_adapter import BedrockAdapter
from sr8.adapters.gemini_adapter import GeminiAdapter
from sr8.adapters.ollama_adapter import OllamaAdapter
from sr8.adapters.openai_adapter import OpenAIAdapter
from sr8.config.provider_settings import load_provider_settings


def create_provider(name: str) -> ProviderAdapter:
    key = name.strip().lower()
    settings = load_provider_settings()
    if key == "openai":
        return OpenAIAdapter(settings.openai)
    if key == "azure_openai":
        return AzureOpenAIAdapter(settings.azure_openai)
    if key == "aws_bedrock":
        return BedrockAdapter(settings.aws_bedrock)
    if key == "anthropic":
        return AnthropicAdapter(settings.anthropic)
    if key == "gemini":
        return GeminiAdapter(settings.gemini)
    if key == "ollama":
        return OllamaAdapter(settings.ollama)
    msg = f"Unknown provider '{name}'."
    raise ValueError(msg)
