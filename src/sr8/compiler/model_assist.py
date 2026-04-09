from __future__ import annotations

import json
from dataclasses import dataclass

from sr8.adapters import create_provider
from sr8.adapters.errors import ProviderNormalizationError
from sr8.adapters.types import ProviderRequest, ProviderResponse
from sr8.extract.confidence import build_confidence_signals
from sr8.extract.signals import ExtractedDimensions
from sr8.extract.trace import build_extraction_trace
from sr8.models.extraction_trace import ExtractionTrace

MODEL_ASSIST_SYSTEM_PROMPT = """
You are extracting SR8 compiler dimensions from a local source directive.
Return strict JSON only with these keys:
objective, scope, exclusions, constraints, context_package, assumptions,
dependencies, success_criteria, output_contract, target_class,
authority_context, governance_flags.
Each collection field must be a JSON array of strings.
governance_flags must be an object with ambiguous, incomplete, requires_human_review.
Do not include markdown fences.
""".strip()


@dataclass(slots=True)
class ModelAssistResult:
    extracted: ExtractedDimensions
    trace: ExtractionTrace
    provider_response: ProviderResponse


def _extract_json_object(text: str) -> dict[str, object]:
    stripped = text.strip()
    if stripped.startswith("```") and "\n" in stripped:
        stripped = stripped.split("\n", 1)[1]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ProviderNormalizationError(
            "model_assist",
            "Provider output did not contain a JSON object.",
        )
    payload = json.loads(stripped[start : end + 1])
    if not isinstance(payload, dict):
        raise ProviderNormalizationError("model_assist", "Provider JSON output must be an object.")
    return payload


def run_model_assisted_extraction(
    normalized_source: str,
    provider_name: str,
    model_name: str,
    timeout_seconds: float = 30.0,
) -> ModelAssistResult:
    provider = create_provider(provider_name)
    response = provider.complete(
        ProviderRequest(
            provider=provider_name,
            model=model_name,
            prompt=normalized_source,
            system_prompt=MODEL_ASSIST_SYSTEM_PROMPT,
            response_format="json",
            timeout_seconds=timeout_seconds,
            metadata={"mode": "model_assisted_extraction"},
        )
    )
    extracted = ExtractedDimensions.model_validate(_extract_json_object(response.content))
    confidence = build_confidence_signals(extracted, inferred_fields=set())
    trace = build_extraction_trace(
        adapter_name="model_assisted",
        confidence=confidence,
        metadata={
            "provider": provider_name,
            "model": model_name,
            "finish_reason": response.finish_reason,
            "assist_extract_status": "assisted",
            "assist_extract_route": "provider_live",
            "fallback": None,
        },
    )
    return ModelAssistResult(extracted=extracted, trace=trace, provider_response=response)
