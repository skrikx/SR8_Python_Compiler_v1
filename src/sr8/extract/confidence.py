from __future__ import annotations

from sr8.extract.signals import ExtractedDimensions
from sr8.models.extraction_confidence import ExtractionConfidenceSignal

WEAK_TOKENS = ("unclear", "tbd", "todo", "various", "something", "stuff", "maybe", "unknown")


def _contains_weak_signal(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in WEAK_TOKENS)


def _text_signal(field_name: str, value: str) -> ExtractionConfidenceSignal:
    if not value.strip():
        return ExtractionConfidenceSignal(
            field_name=field_name,
            status="empty",
            confidence_band="low",
            evidence_summary="No strong extraction evidence.",
        )
    if _contains_weak_signal(value) or len(value.strip()) < 8:
        return ExtractionConfidenceSignal(
            field_name=field_name,
            status="weak",
            confidence_band="low",
            evidence_summary="Field populated from sparse or ambiguous evidence.",
            notes="Input text contains weak or underspecified phrasing.",
        )
    return ExtractionConfidenceSignal(
        field_name=field_name,
        status="explicit",
        confidence_band="high",
        evidence_summary="Field populated from direct section or heading evidence.",
    )


def _list_signal(
    field_name: str,
    values: list[str],
    *,
    contradictory: bool = False,
) -> ExtractionConfidenceSignal:
    if contradictory:
        return ExtractionConfidenceSignal(
            field_name=field_name,
            status="contradictory",
            confidence_band="low",
            evidence_summary="Conflicting items were extracted across related sections.",
            notes="At least one extracted item overlaps with an exclusion.",
        )
    if not values:
        return ExtractionConfidenceSignal(
            field_name=field_name,
            status="empty",
            confidence_band="low",
            evidence_summary="No extracted items.",
        )
    joined = " ".join(values)
    if _contains_weak_signal(joined):
        return ExtractionConfidenceSignal(
            field_name=field_name,
            status="weak",
            confidence_band="low",
            evidence_summary=f"Extracted {len(values)} item(s), but phrasing is weak or ambiguous.",
            notes="Review the extracted items before downstream use.",
        )
    return ExtractionConfidenceSignal(
        field_name=field_name,
        status="explicit",
        confidence_band="high",
        evidence_summary=f"Extracted {len(values)} item(s) from section signals.",
    )


def _governance_signal(extracted: ExtractedDimensions) -> ExtractionConfidenceSignal:
    flags = extracted.governance_flags
    if flags.requires_human_review:
        notes: list[str] = []
        if flags.ambiguous:
            notes.append("ambiguous")
        if flags.incomplete:
            notes.append("incomplete")
        return ExtractionConfidenceSignal(
            field_name="governance_flags",
            status="weak",
            confidence_band="low",
            evidence_summary="Governance flags require human review.",
            notes=", ".join(notes) or "requires_human_review",
        )
    return ExtractionConfidenceSignal(
        field_name="governance_flags",
        status="explicit",
        confidence_band="medium",
        evidence_summary="No governance escalation flags were raised by the extractor.",
    )


def build_confidence_signals(
    extracted: ExtractedDimensions,
    inferred_fields: set[str] | None = None,
) -> list[ExtractionConfidenceSignal]:
    inferred = inferred_fields or set()
    scope_conflict = bool(
        {item.strip().lower() for item in extracted.scope if item.strip()}
        & {item.strip().lower() for item in extracted.exclusions if item.strip()}
    )
    signals = [
        _text_signal("objective", extracted.objective),
        _list_signal("scope", extracted.scope, contradictory=scope_conflict),
        _list_signal("exclusions", extracted.exclusions),
        _list_signal("constraints", extracted.constraints),
        _list_signal("context_package", extracted.context_package),
        _text_signal("target_class", extracted.target_class),
        _text_signal("authority_context", extracted.authority_context),
        _list_signal("dependencies", extracted.dependencies),
        _list_signal("assumptions", extracted.assumptions),
        _list_signal("success_criteria", extracted.success_criteria),
        _list_signal("output_contract", extracted.output_contract),
        _governance_signal(extracted),
    ]
    output: list[ExtractionConfidenceSignal] = []
    for signal in signals:
        if signal.field_name in inferred and signal.status != "empty":
            output.append(
                signal.model_copy(
                    update={
                        "status": "inferred",
                        "confidence_band": "medium",
                        "notes": "Value was inferred from keyword heuristics.",
                    }
                )
            )
            continue
        output.append(signal)
    return output
