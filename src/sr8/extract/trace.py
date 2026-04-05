from __future__ import annotations

from collections import Counter
from collections.abc import Mapping

from sr8.models.extraction_confidence import ExtractionConfidenceSignal
from sr8.models.extraction_trace import ExtractionTrace


def build_extraction_trace(
    adapter_name: str,
    confidence: list[ExtractionConfidenceSignal],
    metadata: dict[str, object] | None = None,
) -> ExtractionTrace:
    return ExtractionTrace(
        adapter_name=adapter_name,
        confidence=confidence,
        metadata=metadata or {},
    )


def coerce_extraction_trace(
    value: ExtractionTrace | Mapping[str, object] | None,
) -> ExtractionTrace | None:
    if value is None:
        return None
    if isinstance(value, ExtractionTrace):
        return value
    return ExtractionTrace.model_validate(value)


def summarize_extraction_trace(
    value: ExtractionTrace | Mapping[str, object] | None,
) -> dict[str, object]:
    trace = coerce_extraction_trace(value)
    if trace is None:
        return {
            "adapter_name": "unknown",
            "status_counts": {},
            "low_confidence_fields": [],
            "provider": None,
        }

    counts = Counter(signal.status for signal in trace.confidence)
    low_confidence_fields = [
        signal.field_name
        for signal in trace.confidence
        if signal.confidence_band == "low" or signal.status in {"weak", "contradictory", "empty"}
    ]
    return {
        "adapter_name": trace.adapter_name,
        "status_counts": dict(sorted(counts.items())),
        "low_confidence_fields": low_confidence_fields,
        "provider": trace.metadata.get("provider"),
    }
