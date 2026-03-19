from __future__ import annotations

from sr8.extract.signals import ExtractedDimensions
from sr8.models.base import SR8Model
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.receipts import CompilationReceipt
from sr8.models.source_intent import SourceIntent
from sr8.version import __version__


class CompileConfig(SR8Model):
    artifact_version: str = "1.0.0"
    compiler_version: str = __version__
    profile: str = "generic"
    include_raw_source: bool = False


class CompilationResult(SR8Model):
    artifact: IntentArtifact
    receipt: CompilationReceipt
    normalized_source: SourceIntent
    extracted_dimensions: ExtractedDimensions
