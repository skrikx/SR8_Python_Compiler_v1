from __future__ import annotations

from collections.abc import Mapping

from sr8.adapters.base import ProviderAdapter, extract_text_content
from sr8.adapters.errors import ProviderNormalizationError
from sr8.adapters.types import ProviderProbeResult, ProviderRequest, ProviderResponse
from sr8.config.provider_settings import AWSBedrockProviderSettings


class BedrockAdapter(ProviderAdapter[AWSBedrockProviderSettings]):
    name = "aws_bedrock"
    label = "AWS Bedrock"
    required_env_vars = ("SR8_AWS_BEDROCK_REGION", "SR8_AWS_BEDROCK_MODEL")
    supports_live_inference = False

    def __init__(self, settings: AWSBedrockProviderSettings) -> None:
        super().__init__(settings)
        self.settings = settings

    def probe(self) -> ProviderProbeResult:
        missing = [name for name in self.required_env_vars if not self._read_env_field(name)]
        configured = not missing
        detail = (
            "Registered only. Live runtime is disabled until SigV4 request signing is implemented."
        )
        if not configured:
            detail = (
                "Missing required environment variables. "
                "Live runtime is also disabled until SigV4 request signing is implemented."
            )
        return ProviderProbeResult(
            provider=self.name,
            registered=True,
            configured=configured,
            capable=True,
            live_enabled=False,
            ready_for_runtime=False,
            available=False,
            supports_live_inference=self.supports_live_inference,
            missing_env_vars=missing,
            detail=detail,
            capabilities=list(self.capabilities),
        )

    def prepare_http_request(
        self,
        request: ProviderRequest,
    ) -> tuple[str, dict[str, str], dict[str, object]]:
        raise ProviderNormalizationError(
            self.name,
            "AWS Bedrock live inference requires SigV4 signing and is not enabled in this runtime.",
        )

    def normalize_response(self, payload: Mapping[str, object]) -> ProviderResponse:
        content = payload.get("outputText")
        if not isinstance(content, str):
            content = extract_text_content(payload.get("content"))
        if not isinstance(content, str):
            raise ProviderNormalizationError(self.name, "Bedrock response missing text content.")
        return ProviderResponse(
            provider=self.name,
            model=str(payload.get("modelId", self.settings.model or "")),
            content=content,
            raw_payload=dict(payload),
        )
