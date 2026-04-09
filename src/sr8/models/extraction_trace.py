from __future__ import annotations

from pydantic import Field

from sr8.models.base import SR8Model
from sr8.models.extraction_confidence import ExtractionConfidenceSignal


class ExtractionRecovery(SR8Model):
    intake_required: bool = False
    missing_fields: list[str] = Field(default_factory=list)
    weak_fields: list[str] = Field(default_factory=list)
    contradictory_fields: list[str] = Field(default_factory=list)
    suggested_prompt: str = ""


class ExtractionTrace(SR8Model):
    adapter_name: str
    confidence: list[ExtractionConfidenceSignal] = Field(default_factory=list)
    recovery: ExtractionRecovery = Field(default_factory=ExtractionRecovery)
    metadata: dict[str, object] = Field(default_factory=dict)
