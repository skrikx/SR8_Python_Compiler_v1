from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict


def utc_now() -> datetime:
    return datetime.now(UTC)


class SR8Model(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
