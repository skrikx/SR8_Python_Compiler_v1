from __future__ import annotations

from datetime import datetime

from pydantic import Field

from sr8.models.base import SR8Model, utc_now


class TransformReceiptRecord(SR8Model):
    receipt_id: str
    parent_artifact_id: str
    derivative_id: str
    transform_target: str
    profile: str
    created_at: datetime = Field(default_factory=utc_now)
    renderer_version: str
    output_path: str
