from __future__ import annotations

from typing import Literal

from sr8.models.base import SR8Model

ConfidenceBand = Literal["high", "medium", "low"]
FieldStatus = Literal["explicit", "inferred", "weak", "empty", "contradictory"]


class ExtractionConfidenceSignal(SR8Model):
    field_name: str
    status: FieldStatus
    confidence_band: ConfidenceBand
    evidence_summary: str
    notes: str = ""
