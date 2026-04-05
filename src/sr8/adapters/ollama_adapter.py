from __future__ import annotations

from collections.abc import Mapping

from sr8.adapters.base import ProviderAdapter, extract_text_content
from sr8.adapters.errors import ProviderNormalizationError
from sr8.adapters.types import ProviderProbeResult, ProviderRequest, ProviderResponse
from sr8.config.provider_settings import OllamaProviderSettings


class OllamaAdapter(ProviderAdapter[OllamaProviderSettings]):
    name = "ollama"
    label = "Ollama"
    required_env_vars = ("SR8_OLLAMA_MODEL",)

    def __init__(self, settings: OllamaProviderSettings) -> None:
        super().__init__(settings)
        self.settings = settings

    def probe(self) -> ProviderProbeResult:
        result = super().probe()
        return result.model_copy(update={"available": True})

    def prepare_http_request(
        self,
        request: ProviderRequest,
    ) -> tuple[str, dict[str, str], dict[str, object]]:
        payload = {
            "model": request.model,
            "prompt": f"{request.system_prompt}\n\n{request.prompt}".strip(),
            "stream": False,
            "format": "json" if request.response_format == "json" else "",
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }
        return (
            f"{self.settings.base_url.rstrip('/')}/api/generate",
            {"Content-Type": "application/json"},
            payload,
        )

    def normalize_response(self, payload: Mapping[str, object]) -> ProviderResponse:
        response_text = payload.get("response")
        if not isinstance(response_text, str):
            message = payload.get("message")
            if isinstance(message, Mapping):
                response_text = extract_text_content(message.get("content"))
        if not isinstance(response_text, str):
            raise ProviderNormalizationError(self.name, "Ollama response missing text content.")
        return ProviderResponse(
            provider=self.name,
            model=str(payload.get("model", self.settings.model or "")),
            content=response_text,
            finish_reason="stop",
            raw_payload=dict(payload),
        )
