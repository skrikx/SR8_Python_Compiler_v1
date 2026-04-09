from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model, utc_now

AsyncJobStatus = Literal["queued", "running", "completed", "failed"]


class AsyncJobError(SR8Model):
    code: str
    message: str
    details: dict[str, object] = Field(default_factory=dict)


class AsyncJobRecord(SR8Model):
    job_id: str
    operation: str
    status: AsyncJobStatus
    request_hash: str
    workspace_root: str
    actor_id: str
    idempotency_key: str | None = None
    attempts: int = 0
    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result_payload: dict[str, object] | None = None
    error: AsyncJobError | None = None
