from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model, utc_now
from sr8.models.lint_finding import LintFinding


class LintReport(SR8Model):
    report_id: str
    artifact_ref: str
    status: Literal["pass", "warn", "fail"]
    summary: str
    findings: list[LintFinding] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
