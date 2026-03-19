from __future__ import annotations

from typing import Literal

from sr8.models.base import SR8Model


class LintFinding(SR8Model):
    rule_id: str
    severity: Literal["info", "warn", "error"]
    message: str
    artifact_field: str
    suggested_fix: str
