from __future__ import annotations

from datetime import datetime

from pydantic import Field

from sr8.models.base import SR8Model, utc_now


class CompilationReceiptRecord(SR8Model):
    receipt_id: str
    artifact_id: str
    compiler_version: str
    source_hash: str
    compile_run_id: str
    profile: str
    target_class: str
    created_at: datetime = Field(default_factory=utc_now)
    extracted_dimensions_summary: dict[str, object] = Field(default_factory=dict)
    extraction_trust_summary: dict[str, object] = Field(default_factory=dict)
    recovery_summary: dict[str, object] = Field(default_factory=dict)
    lineage_summary: dict[str, object] = Field(default_factory=dict)
    validation_summary: str
    warnings: list[str] = Field(default_factory=list)
    output_path: str
