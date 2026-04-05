from __future__ import annotations

from sr8.extract.signals import ExtractedDimensions
from sr8.models.base import SR8Model
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.receipts import CompilationReceipt
from sr8.models.source_intent import SourceIntent


class CompilationResult(SR8Model):
    artifact: IntentArtifact
    receipt: CompilationReceipt
    normalized_source: SourceIntent
    extracted_dimensions: ExtractedDimensions
