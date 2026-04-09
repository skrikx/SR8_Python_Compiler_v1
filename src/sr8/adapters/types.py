from __future__ import annotations

from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model

ProviderName = Literal[
    "openai",
    "azure_openai",
    "aws_bedrock",
    "anthropic",
    "gemini",
    "ollama",
]
ProviderRuntimeTransport = Literal["http", "sdk"]
ProviderProbeStatus = Literal["ready", "bounded", "degraded", "missing_config"]


class ProviderRequest(SR8Model):
    provider: str
    model: str
    prompt: str
    system_prompt: str = ""
    temperature: float = 0.0
    max_tokens: int = 1200
    response_format: Literal["text", "json"] = "json"
    timeout_seconds: float = 30.0
    metadata: dict[str, object] = Field(default_factory=dict)


class ProviderResponse(SR8Model):
    provider: str
    model: str
    content: str
    finish_reason: str = "stop"
    usage: dict[str, int] = Field(default_factory=dict)
    raw_payload: dict[str, object] = Field(default_factory=dict)


class ProviderDescriptor(SR8Model):
    name: str
    label: str
    capabilities: list[str] = Field(default_factory=list)
    required_env_vars: list[str] = Field(default_factory=list)
    default_model_env_var: str | None = None
    runtime_transport: ProviderRuntimeTransport = "http"
    assist_extract_supported: bool = True
    supports_live_inference: bool = True
    optional: bool = True


class ProviderProbeResult(SR8Model):
    provider: str
    status: ProviderProbeStatus = "missing_config"
    registered: bool = True
    configured: bool
    subscribed_or_accessible: bool | None = None
    capable: bool = True
    live_enabled: bool
    ready_for_runtime: bool
    available: bool
    supports_live_inference: bool
    configured_model: str | None = None
    requires_live_probe: bool = False
    missing_env_vars: list[str] = Field(default_factory=list)
    detail: str = ""
    capabilities: list[str] = Field(default_factory=list)
