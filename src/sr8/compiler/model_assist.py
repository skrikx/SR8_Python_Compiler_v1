from __future__ import annotations

import json
from dataclasses import dataclass

from pydantic import ValidationError

from sr8.adapters import create_provider
from sr8.adapters.errors import ProviderNormalizationError
from sr8.adapters.types import ProviderRequest, ProviderResponse
from sr8.extract.confidence import build_confidence_signals
from sr8.extract.signals import ExtractedDimensions
from sr8.extract.trace import build_extraction_trace
from sr8.models.extraction_trace import ExtractionTrace
from sr8.utils.hash import stable_object_hash, stable_text_hash

PROMPT_TEMPLATE_ID = "sr8.model_assist.extract.v1"
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


def _extract_json_object(text: str) -> tuple[dict[str, object], int]:
    repair_attempts = 0
    stripped = text.strip()
    if stripped.startswith("```") and "\n" in stripped:
        repair_attempts += 1
        stripped = stripped.split("\n", 1)[1]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ProviderNormalizationError(
            "model_assist",
            "Provider output did not contain a JSON object.",
        )
    if start != 0 or end != len(stripped) - 1:
        repair_attempts += 1
    payload = json.loads(stripped[start : end + 1])
    if not isinstance(payload, dict):
        raise ProviderNormalizationError("model_assist", "Provider JSON output must be an object.")
    return payload, repair_attempts


def run_model_assisted_extraction(
    normalized_source: str,
    provider_name: str,
    model_name: str,
    timeout_seconds: float = 30.0,
) -> ModelAssistResult:
    provider = create_provider(provider_name)
    prompt_hash = stable_text_hash(f"{MODEL_ASSIST_SYSTEM_PROMPT}\n\n{normalized_source}")
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
    try:
        candidate_payload, repair_attempts = _extract_json_object(response.content)
    except json.JSONDecodeError as exc:
        raise ProviderNormalizationError(
            "model_assist",
            f"Provider JSON output was invalid: {exc.msg}.",
        ) from exc
    try:
        extracted = ExtractedDimensions.model_validate(candidate_payload)
    except ValidationError as exc:
        raise ProviderNormalizationError(
            "model_assist",
            f"Provider JSON failed SR8 extraction schema validation: {exc.errors()[0]['msg']}.",
        ) from exc
    confidence = build_confidence_signals(extracted, inferred_fields=set())
    trace = build_extraction_trace(
        adapter_name="model_assisted",
        confidence=confidence,
        metadata={
            "provider": provider_name,
            "model": model_name,
            "prompt_template_id": PROMPT_TEMPLATE_ID,
            "prompt_hash": prompt_hash,
            "raw_response_hash": stable_text_hash(response.content),
            "parsed_response_hash": stable_object_hash(candidate_payload),
            "repair_attempts": repair_attempts,
            "schema_validation_status": "pass",
            "finish_reason": response.finish_reason,
            "assist_extract_status": "assisted",
            "assist_extract_route": "provider_live",
            "fallback": None,
        },
    )
    return ModelAssistResult(extracted=extracted, trace=trace, provider_response=response)
