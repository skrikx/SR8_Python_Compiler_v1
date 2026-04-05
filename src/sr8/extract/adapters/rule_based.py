from __future__ import annotations

from typing import TYPE_CHECKING

from sr8.extract.adapters.base import ExtractionAdapter
from sr8.extract.confidence import build_confidence_signals
from sr8.extract.core import extract_dimensions
from sr8.extract.rules import infer_authority_context, infer_target_class
from sr8.extract.signals import ExtractedDimensions
from sr8.extract.trace import build_extraction_trace
from sr8.models.extraction_trace import ExtractionTrace

if TYPE_CHECKING:
    from sr8.models.compile_config import CompileConfig


class RuleBasedExtractionAdapter(ExtractionAdapter):
    name = "rule_based"

    def extract(
        self,
        normalized_source: str,
        config: CompileConfig | None = None,
    ) -> tuple[ExtractedDimensions, ExtractionTrace]:
        extracted = extract_dimensions(normalized_source)
        inferred_fields: set[str] = set()
        if (
            extracted.target_class
            and infer_target_class(normalized_source) == extracted.target_class
        ):
            inferred_fields.add("target_class")
        if (
            extracted.authority_context
            and infer_authority_context(normalized_source) == extracted.authority_context
        ):
            inferred_fields.add("authority_context")
        confidence = build_confidence_signals(extracted, inferred_fields=inferred_fields)
        return extracted, build_extraction_trace(self.name, confidence)
