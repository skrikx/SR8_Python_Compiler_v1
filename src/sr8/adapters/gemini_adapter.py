from __future__ import annotations

from collections.abc import Mapping

from sr8.adapters.base import ProviderAdapter, extract_text_content
from sr8.adapters.errors import ProviderNormalizationError
from sr8.adapters.types import ProviderRequest, ProviderResponse
from sr8.config.provider_settings import GeminiProviderSettings


class GeminiAdapter(ProviderAdapter[GeminiProviderSettings]):
    name = "gemini"
    label = "Gemini"
    required_env_vars = ("SR8_GEMINI_API_KEY", "SR8_GEMINI_MODEL")

    def __init__(self, settings: GeminiProviderSettings) -> None:
        super().__init__(settings)
        self.settings = settings

    def prepare_http_request(
        self,
        request: ProviderRequest,
    ) -> tuple[str, dict[str, str], dict[str, object]]:
        url = (
            f"{self.settings.base_url.rstrip('/')}/models/{request.model}:generateContent"
            f"?key={self.settings.api_key}"
        )
        payload: dict[str, object] = {
            "systemInstruction": {"parts": [{"text": request.system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": request.prompt}]}],
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens,
            },
        }
        return url, {"Content-Type": "application/json"}, payload

    def normalize_response(self, payload: Mapping[str, object]) -> ProviderResponse:
        candidates = payload.get("candidates")
        if not isinstance(candidates, list) or not candidates:
            raise ProviderNormalizationError(self.name, "Gemini response missing candidates.")
        first = candidates[0]
        if not isinstance(first, Mapping):
            raise ProviderNormalizationError(self.name, "Gemini candidate payload is invalid.")
        content = first.get("content")
        if not isinstance(content, Mapping):
            raise ProviderNormalizationError(self.name, "Gemini response missing content block.")
        return ProviderResponse(
            provider=self.name,
            model=str(payload.get("modelVersion", self.settings.model or "")),
            content=extract_text_content(content.get("parts")),
            finish_reason=str(first.get("finishReason", "stop")),
            raw_payload=dict(payload),
        )
