from __future__ import annotations

from sr8.adapters.factory import create_provider
from sr8.adapters.types import ProviderDescriptor, ProviderProbeResult

PROVIDER_NAMES = (
    "openai",
    "azure_openai",
    "aws_bedrock",
    "anthropic",
    "gemini",
    "ollama",
)


def list_provider_names() -> tuple[str, ...]:
    return PROVIDER_NAMES


def list_provider_descriptors() -> list[ProviderDescriptor]:
    return [create_provider(name).describe() for name in PROVIDER_NAMES]


def get_provider_descriptor(name: str) -> ProviderDescriptor:
    return create_provider(name).describe()


def probe_provider(name: str) -> ProviderProbeResult:
    return create_provider(name).probe()


def probe_providers() -> list[ProviderProbeResult]:
    return [probe_provider(name) for name in PROVIDER_NAMES]
