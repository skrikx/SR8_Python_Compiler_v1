from __future__ import annotations

from datetime import datetime

from pydantic import Field

from sr8.models.base import SR8Model
from sr8.models.lineage import Lineage
from sr8.models.source_intent import SourceType
from sr8.models.validation import ValidationReport


class ArtifactSource(SR8Model):
    source_id: str
    source_type: SourceType
    source_hash: str
    origin: str | None = None


class GovernanceFlags(SR8Model):
    ambiguous: bool = False
    incomplete: bool = False
    requires_human_review: bool = False


class IntentArtifact(SR8Model):
    artifact_id: str
    artifact_version: str
    compiler_version: str
    profile: str = "generic"
    created_at: datetime
    source: ArtifactSource
    objective: str = ""
    scope: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    context_package: list[str] = Field(default_factory=list)
    target_class: str = ""
    authority_context: str = ""
    dependencies: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    output_contract: list[str] = Field(default_factory=list)
    governance_flags: GovernanceFlags = Field(default_factory=GovernanceFlags)
    validation: ValidationReport
    lineage: Lineage
    metadata: dict[str, object] = Field(default_factory=dict)
