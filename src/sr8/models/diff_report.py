from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model, utc_now


class DiffFieldChange(SR8Model):
    field: str
    change_class: Literal["added", "removed", "modified", "unchanged"]
    impact: Literal["low", "medium", "high"]
    semantic_class: Literal["breaking", "additive", "editorial", "unchanged"] = "unchanged"
    left: object | None = None
    right: object | None = None
    note: str = ""


class DiffReport(SR8Model):
    report_id: str
    left_ref: str
    right_ref: str
    summary: str
    changes: list[DiffFieldChange] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
