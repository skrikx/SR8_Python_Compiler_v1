from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model, utc_now


class CompilationReceipt(SR8Model):
    receipt_id: str
    artifact_id: str
    source_hash: str
    compile_run_id: str = ""
    status: Literal["accepted", "rejected"] = "accepted"
    notes: list[str] = Field(default_factory=list)
    parent_artifact_ids: list[str] = Field(default_factory=list)
    compile_kind: Literal[
        "semantic_compile",
        "canonicalize_structured",
        "needs_intake",
    ] = "canonicalize_structured"
    semantic_transform_applied: bool = False
    source_structure_kind: str = "raw_text"
    source_supplied_fields: list[str] = Field(default_factory=list)
    compiler_derived_fields: list[str] = Field(default_factory=list)
    unresolved_fields: list[str] = Field(default_factory=list)
    derived_field_count: int = 0
    source_supplied_field_count: int = 0
    assist_route: str = "not_used"
    intake_route: str = "not_required"
    compile_truth_summary: str = ""
    compiled_at: datetime = Field(default_factory=utc_now)
