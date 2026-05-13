from __future__ import annotations

from typing import TYPE_CHECKING

from sr8.adapters.errors import ProviderError
from sr8.compiler.model_assist import MODEL_ASSIST_SYSTEM_PROMPT, run_model_assisted_extraction
from sr8.config.settings import SR8Settings
from sr8.extract.adapters.base import ExtractionAdapter
from sr8.extract.adapters.rule_based import RuleBasedExtractionAdapter
from sr8.extract.signals import ExtractedDimensions
from sr8.models.extraction_trace import ExtractionTrace

if TYPE_CHECKING:
    from sr8.models.compile_config import CompileConfig


class ModelAssistedExtractionAdapter(ExtractionAdapter):
    name = "model_assisted"

    def _fallback_metadata(
        self,
        *,
        provider_name: str,
        model_name: str,
        exc: ProviderError,
        trace: ExtractionTrace,
    ) -> dict[str, object]:
        return {
            **trace.metadata,
            "provider": provider_name,
            "model": model_name,
            "fallback": "rule_based",
            "assist_extract_status": "fallback_rule_based",
            "assist_extract_route": "provider_failed_then_rule_based",
            "error_type": type(exc).__name__,
            "error_message": str(exc)[:240],
        }

    def extract(
        self,
        normalized_source: str,
        config: CompileConfig | None = None,
    ) -> tuple[ExtractedDimensions, ExtractionTrace]:
        settings = SR8Settings()
        provider_name = (
            config.assist_provider
            if config and config.assist_provider
            else settings.assist_provider
        )
        model_name = (
            config.assist_model if config and config.assist_model else settings.assist_model
        )
        if not provider_name or not model_name:
            msg = "Model-assisted extraction requires assist_provider and assist_model."
            raise ValueError(msg)
        try:
            result = run_model_assisted_extraction(
                normalized_source=normalized_source,
                provider_name=provider_name,
                model_name=model_name,
            )
            if config is not None and config.save_llm_trace:
                result.trace.metadata.update(
                    {
                        "raw_prompt": normalized_source,
                        "raw_system_prompt": MODEL_ASSIST_SYSTEM_PROMPT,
                        "raw_response": result.provider_response.content,
                    }
                )
            return result.extracted, result.trace
        except ProviderError as exc:
            if config is not None and not config.assist_fallback_to_rule_based:
                raise
            extracted, trace = RuleBasedExtractionAdapter().extract(
                normalized_source,
                config=config,
            )
            return extracted, trace.model_copy(
                update={
                    "adapter_name": f"model_assisted:{provider_name}:fallback:rule_based",
                    "metadata": self._fallback_metadata(
                        provider_name=provider_name,
                        model_name=model_name,
                        exc=exc,
                        trace=trace,
                    ),
                }
            )
