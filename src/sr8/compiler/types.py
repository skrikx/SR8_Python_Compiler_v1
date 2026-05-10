from __future__ import annotations

from pydantic import Field

from sr8.extract.signals import ExtractedDimensions
from sr8.models.base import SR8Model
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.receipts import CompilationReceipt
from sr8.models.source_intent import SourceIntent


class CompileTargetValidation(SR8Model):
    target: str
    output_format: str
    content: str
    valid: bool
    status: str
    artifact_type: str = ""
    depth_tier: str = ""
    errors: list[dict[str, object]] = Field(default_factory=list)
    warnings: list[dict[str, object]] = Field(default_factory=list)
    repair_actions: list[str] = Field(default_factory=list)


class CompilationResult(SR8Model):
    artifact: IntentArtifact
    receipt: CompilationReceipt
    normalized_source: SourceIntent
    extracted_dimensions: ExtractedDimensions
    target_validation: CompileTargetValidation | None = None
