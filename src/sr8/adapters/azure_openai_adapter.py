from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from sr8.adapters.base import ProviderAdapter, extract_text_content
from sr8.adapters.errors import ProviderNormalizationError
from sr8.adapters.types import ProviderRequest, ProviderResponse
from sr8.config.provider_settings import AzureOpenAIProviderSettings


class AzureOpenAIAdapter(ProviderAdapter[AzureOpenAIProviderSettings]):
    name = "azure_openai"
    label = "Azure OpenAI"
    required_env_vars = (
        "SR8_AZURE_OPENAI_API_KEY",
        "SR8_AZURE_OPENAI_ENDPOINT",
        "SR8_AZURE_OPENAI_DEPLOYMENT",
    )

    def __init__(self, settings: AzureOpenAIProviderSettings) -> None:
        super().__init__(settings)
        self.settings = settings

    def prepare_http_request(
        self,
        request: ProviderRequest,
    ) -> tuple[str, dict[str, str], dict[str, object]]:
        if self.settings.endpoint is None or self.settings.deployment is None:
            raise ProviderNormalizationError(
                self.name,
                "Azure OpenAI endpoint or deployment is missing.",
            )
        url = (
            f"{self.settings.endpoint.rstrip('/')}/openai/deployments/"
            f"{self.settings.deployment}/chat/completions?api-version={self.settings.api_version}"
        )
        headers = {"api-key": str(self.settings.api_key), "Content-Type": "application/json"}
        payload: dict[str, object] = {
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.prompt},
            ],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        if request.response_format == "json":
            payload["response_format"] = {"type": "json_object"}
        return url, headers, payload

    def normalize_response(self, payload: Mapping[str, object]) -> ProviderResponse:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ProviderNormalizationError(self.name, "Azure OpenAI response missing choices.")
        choice = cast(Mapping[str, object], choices[0])
        message = choice.get("message")
        if not isinstance(message, Mapping):
            raise ProviderNormalizationError(
                self.name,
                "Azure OpenAI response missing message payload.",
            )
        usage = payload.get("usage")
        return ProviderResponse(
            provider=self.name,
            model=str(payload.get("model", self.settings.model or "")),
            content=extract_text_content(message.get("content")),
            finish_reason=str(choice.get("finish_reason", "stop")),
            usage=cast(dict[str, int], usage) if isinstance(usage, dict) else {},
            raw_payload=dict(payload),
        )
