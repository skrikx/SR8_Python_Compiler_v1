from __future__ import annotations

from datetime import datetime
from typing import Literal

from sr8.models.base import SR8Model


class ArtifactRecord(SR8Model):
    record_id: str
    artifact_id: str
    artifact_kind: Literal["canonical", "derivative"]
    profile: str
    target_class: str
    transform_target: str | None = None
    source_hash: str
    created_at: datetime
    file_path: str
    parent_artifact_id: str | None = None
    readiness_status: str
