from __future__ import annotations

from pydantic import Field

from sr8.models.base import SR8Model
from sr8.models.extraction_confidence import ExtractionConfidenceSignal


class ExtractionTrace(SR8Model):
    adapter_name: str
    confidence: list[ExtractionConfidenceSignal] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)
