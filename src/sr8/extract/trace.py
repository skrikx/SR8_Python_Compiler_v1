from __future__ import annotations

from collections import Counter
from collections.abc import Mapping

from sr8.models.extraction_confidence import ExtractionConfidenceSignal
from sr8.models.extraction_trace import ExtractionRecovery, ExtractionTrace

RECOVERY_IMPORTANT_FIELDS = (
    "objective",
    "scope",
    "constraints",
    "success_criteria",
    "output_contract",
)

RECOVERY_LABELS = {
    "objective": "Objective",
    "scope": "Scope",
    "constraints": "Constraints",
    "success_criteria": "Success Criteria",
    "output_contract": "Output Contract",
}


def build_extraction_recovery(
    confidence: list[ExtractionConfidenceSignal],
) -> ExtractionRecovery:
    missing_fields = [
        signal.field_name
        for signal in confidence
        if signal.field_name in RECOVERY_IMPORTANT_FIELDS and signal.status == "empty"
    ]
    weak_fields = [
        signal.field_name
        for signal in confidence
        if signal.field_name in RECOVERY_IMPORTANT_FIELDS and signal.status in {"weak", "inferred"}
    ]
    contradictory_fields = [
        signal.field_name
        for signal in confidence
        if signal.status == "contradictory"
    ]
    intake_required = bool(contradictory_fields) or "objective" in missing_fields or (
        len(missing_fields) + len(weak_fields) >= 3
    )
    suggested_prompt = ""
    if intake_required:
        needed = [
            RECOVERY_LABELS[field]
            for field in RECOVERY_IMPORTANT_FIELDS
            if field in missing_fields or field in weak_fields
        ]
        if contradictory_fields:
            needed.append("Resolve contradictions")
        joined = ", ".join(dict.fromkeys(needed))
        suggested_prompt = (
            f"Provide a stronger intent package with explicit {joined}."
            if joined
            else (
                "Provide a stronger intent package with explicit objective, "
                "scope, constraints, success criteria, and output contract."
            )
        )
    return ExtractionRecovery(
        intake_required=intake_required,
        missing_fields=missing_fields,
        weak_fields=weak_fields,
        contradictory_fields=contradictory_fields,
        suggested_prompt=suggested_prompt,
    )


def build_extraction_trace(
    adapter_name: str,
    confidence: list[ExtractionConfidenceSignal],
    metadata: dict[str, object] | None = None,
) -> ExtractionTrace:
    return ExtractionTrace(
        adapter_name=adapter_name,
        confidence=confidence,
        recovery=build_extraction_recovery(confidence),
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
            "intake_required": False,
            "recovery": ExtractionRecovery().model_dump(mode="json"),
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
        "intake_required": trace.recovery.intake_required,
        "recovery": trace.recovery.model_dump(mode="json"),
    }
