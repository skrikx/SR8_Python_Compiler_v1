from __future__ import annotations

from typing import Literal

from pydantic import Field

from sr8.extract.signals import ExtractedDimensions
from sr8.models.base import SR8Model
from sr8.models.compile_config import CompileConfig
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.receipts import CompilationReceipt
from sr8.models.source_intent import SourceIntent

FrontdoorStatus = Literal["compiled", "intake_required", "safe_alternative"]
GovernanceStatus = Literal["allow", "deny", "safe_alternative_compile"]


class GovernanceDecision(SR8Model):
    status: GovernanceStatus
    reason: str
    notes: list[str] = Field(default_factory=list)


class FrontdoorCompileResult(SR8Model):
    status: FrontdoorStatus
    entry_mode: str
    artifact_family: str
    delivery_target: str
    governance: GovernanceDecision
    artifact: IntentArtifact | None = None
    receipt: CompilationReceipt | None = None
    normalized_source: SourceIntent | None = None
    extracted_dimensions: ExtractedDimensions | None = None
    intake_xml: str | None = None
    promptunit_package_xml: str | None = None
    sr8_prompt_xml: str | None = None
    safe_alternative_package_xml: str | None = None
    compile_config: CompileConfig | None = None
