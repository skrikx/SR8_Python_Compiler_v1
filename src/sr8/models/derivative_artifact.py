from __future__ import annotations

from datetime import datetime

from pydantic import Field

from sr8.models.base import SR8Model


class DerivativeLineage(SR8Model):
    parent_source_hash: str
    parent_compile_run_id: str
    parent_lineage_steps: list[str] = Field(default_factory=list)


class DerivativeArtifact(SR8Model):
    derivative_id: str
    parent_artifact_id: str
    parent_artifact_version: str
    transform_target: str
    profile: str
    created_at: datetime
    content: str
    lineage: DerivativeLineage
    metadata: dict[str, object] = Field(default_factory=dict)
