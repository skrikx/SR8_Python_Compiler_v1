from __future__ import annotations

from datetime import datetime

from pydantic import Field

from sr8.models.base import SR8Model, utc_now


class LineageStep(SR8Model):
    stage: str
    detail: str
    occurred_at: datetime = Field(default_factory=utc_now)


class Lineage(SR8Model):
    compile_run_id: str
    pipeline_version: str
    source_hash: str
    parent_source_hash: str | None = None
    parent_compile_run_id: str | None = None
    steps: list[LineageStep] = Field(default_factory=list)
    parent_artifact_ids: list[str] = Field(default_factory=list)
