from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from sr8.adapters.base import ProviderAdapter, extract_text_content
from sr8.adapters.errors import ProviderNormalizationError
from sr8.adapters.types import ProviderRequest, ProviderResponse
from sr8.config.provider_settings import AnthropicProviderSettings


class AnthropicAdapter(ProviderAdapter[AnthropicProviderSettings]):
    name = "anthropic"
    label = "Anthropic"
    required_env_vars = ("SR8_ANTHROPIC_API_KEY", "SR8_ANTHROPIC_MODEL")
    default_model_env_var = "SR8_ANTHROPIC_MODEL"

    def __init__(self, settings: AnthropicProviderSettings) -> None:
        super().__init__(settings)
        self.settings = settings

    def prepare_http_request(
        self,
        request: ProviderRequest,
    ) -> tuple[str, dict[str, str], dict[str, object]]:
        headers = {
            "x-api-key": str(self.settings.api_key),
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": request.model,
            "system": request.system_prompt,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        return f"{self.settings.base_url.rstrip('/')}/messages", headers, payload

    def normalize_response(self, payload: Mapping[str, object]) -> ProviderResponse:
        content = payload.get("content")
        if not isinstance(content, list):
            raise ProviderNormalizationError(
                self.name,
                "Anthropic response missing content blocks.",
            )
        usage = payload.get("usage")
        return ProviderResponse(
            provider=self.name,
            model=str(payload.get("model", self.settings.model or "")),
            content=extract_text_content(content),
            finish_reason=str(payload.get("stop_reason", "stop")),
            usage=cast(dict[str, int], usage) if isinstance(usage, dict) else {},
            raw_payload=dict(payload),
        )
