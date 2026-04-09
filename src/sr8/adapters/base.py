from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Generic, TypeVar

import httpx
from pydantic_settings import BaseSettings

from sr8.adapters.errors import (
    ProviderExecutionError,
    ProviderNormalizationError,
    ProviderNotConfiguredError,
    map_http_error,
)
from sr8.adapters.types import (
    ProviderDescriptor,
    ProviderProbeResult,
    ProviderProbeStatus,
    ProviderRequest,
    ProviderResponse,
    ProviderRuntimeTransport,
)

TProviderSettings = TypeVar("TProviderSettings", bound=BaseSettings)


class ProviderAdapter(ABC, Generic[TProviderSettings]):
    name: str
    label: str
    required_env_vars: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ("text_generation", "structured_output")
    default_model_env_var: str | None = None
    runtime_transport: ProviderRuntimeTransport = "http"
    assist_extract_supported: bool = True
    supports_live_inference: bool = True

    def __init__(self, settings: TProviderSettings) -> None:
        self.settings = settings

    def describe(self) -> ProviderDescriptor:
        return ProviderDescriptor(
            name=self.name,
            label=self.label,
            capabilities=list(self.capabilities),
            required_env_vars=list(self.required_env_vars),
            default_model_env_var=self.default_model_env_var,
            runtime_transport=self.runtime_transport,
            assist_extract_supported=self.assist_extract_supported,
            supports_live_inference=self.supports_live_inference,
        )

    def probe(self) -> ProviderProbeResult:
        missing = [name for name in self.required_env_vars if not self._read_env_field(name)]
        configured = not missing
        live_enabled = self.supports_live_inference
        ready_for_runtime = configured and live_enabled
        status: ProviderProbeStatus
        if ready_for_runtime:
            status = "ready"
            detail = "Ready for runtime."
        elif configured:
            status = "bounded"
            detail = "Configured, but live runtime is disabled."
        else:
            status = "missing_config"
            detail = "Missing required environment variables."
        return ProviderProbeResult(
            provider=self.name,
            status=status,
            registered=True,
            configured=configured,
            capable=True,
            live_enabled=live_enabled,
            ready_for_runtime=ready_for_runtime,
            available=ready_for_runtime,
            supports_live_inference=self.supports_live_inference,
            configured_model=getattr(self.settings, "model", None),
            requires_live_probe=False,
            missing_env_vars=missing,
            detail=detail,
            capabilities=list(self.capabilities),
        )

    def complete(self, request: ProviderRequest) -> ProviderResponse:
        if not self.supports_live_inference:
            raise ProviderExecutionError(
                self.name,
                f"{self.name} is registered for normalization and probing only in this runtime.",
            )
        probe = self.probe()
        if not probe.configured:
            missing = ", ".join(probe.missing_env_vars)
            raise ProviderNotConfiguredError(
                self.name,
                f"{self.name} is not configured. Missing: {missing}",
            )
        url, headers, payload = self.prepare_http_request(request)
        try:
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=request.timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise map_http_error(self.name, exc) from exc

        try:
            raw_payload = response.json()
        except ValueError as exc:
            raise ProviderNormalizationError(
                self.name,
                "Provider returned non-JSON payload.",
            ) from exc
        if not isinstance(raw_payload, dict):
            raise ProviderNormalizationError(self.name, "Provider response must be a JSON object.")
        return self.normalize_response(raw_payload)

    def _read_env_field(self, env_name: str) -> str | None:
        field_name = env_name.removeprefix("SR8_").lower()
        field_name = field_name.replace("azure_openai_", "")
        field_name = field_name.replace("aws_bedrock_", "")
        field_name = field_name.replace("openai_", "")
        field_name = field_name.replace("anthropic_", "")
        field_name = field_name.replace("gemini_", "")
        field_name = field_name.replace("ollama_", "")
        value = getattr(self.settings, field_name, None)
        return value if isinstance(value, str) and value else None

    @abstractmethod
    def prepare_http_request(
        self,
        request: ProviderRequest,
    ) -> tuple[str, dict[str, str], dict[str, object]]:
        raise NotImplementedError

    @abstractmethod
    def normalize_response(self, payload: Mapping[str, object]) -> ProviderResponse:
        raise NotImplementedError


def extract_text_content(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text_value = item.get("text")
                if isinstance(text_value, str):
                    parts.append(text_value)
        return "\n".join(part for part in parts if part)
    return ""
