from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model, utc_now


class CompilationReceipt(SR8Model):
    receipt_id: str
    artifact_id: str
    source_hash: str
    status: Literal["accepted", "rejected"] = "accepted"
    notes: list[str] = Field(default_factory=list)
    compiled_at: datetime = Field(default_factory=utc_now)
