from __future__ import annotations

from typing import Literal

from sr8.models.base import utc_now
from sr8.models.validation import ValidationIssue, ValidationReport
from sr8.utils.ids import build_receipt_id


def build_validation_report(
    artifact_id: str,
    source_hash: str,
    errors: list[ValidationIssue],
    warnings: list[ValidationIssue],
) -> ValidationReport:
    readiness_status: Literal["pass", "warn", "fail"]
    if errors:
        readiness_status = "fail"
    elif warnings:
        readiness_status = "warn"
    else:
        readiness_status = "pass"

    summary = (
        f"Validation {readiness_status}: {len(errors)} error(s), {len(warnings)} warning(s)."
    )
    return ValidationReport(
        report_id=build_receipt_id(artifact_id, f"validation:{source_hash}"),
        readiness_status=readiness_status,
        summary=summary,
        errors=errors,
        warnings=warnings,
        generated_at=utc_now(),
    )
