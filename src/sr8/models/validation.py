from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model, utc_now


class ValidationIssue(SR8Model):
    code: str
    message: str
    severity: Literal["info", "warning", "error"] = "error"
    path: str | None = None


class ValidationReport(SR8Model):
    report_id: str
    readiness_status: Literal["pass", "warn", "fail"] = "warn"
    summary: str = ""
    errors: list[ValidationIssue] = Field(default_factory=list)
    warnings: list[ValidationIssue] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)
