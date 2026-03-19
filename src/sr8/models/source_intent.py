from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model, utc_now

SourceType = Literal["text", "markdown", "json", "yaml"]


class SourceIntent(SR8Model):
    source_id: str
    source_type: SourceType
    raw_content: str
    normalized_content: str = ""
    source_hash: str = ""
    origin: str | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    ingested_at: datetime = Field(default_factory=utc_now)
