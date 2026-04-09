from __future__ import annotations

from typing import cast

from sr8.diff.classifiers import classify_change, classify_impact, classify_semantic_change
from sr8.diff.types import SEMANTIC_FIELDS
from sr8.models.diff_report import DiffFieldChange, DiffReport
from sr8.models.intent_artifact import IntentArtifact
from sr8.utils.hash import stable_text_hash


def _read_field(artifact: IntentArtifact, field: str) -> object | None:
    if field == "validation.readiness_status":
        return artifact.validation.readiness_status
    return cast(object | None, getattr(artifact, field))


def semantic_diff(
    left: IntentArtifact,
    right: IntentArtifact,
    left_ref: str,
    right_ref: str,
) -> DiffReport:
    changes: list[DiffFieldChange] = []
    changed_fields: list[str] = []
    semantic_counts = {"breaking": 0, "additive": 0, "editorial": 0}

    for field in SEMANTIC_FIELDS:
        left_value = _read_field(left, field)
        right_value = _read_field(right, field)
        change_class = classify_change(left_value, right_value)
        impact = classify_impact(field, change_class)
        semantic_class = classify_semantic_change(field, change_class, left_value, right_value)
        if change_class != "unchanged":
            changed_fields.append(field)
            semantic_counts[semantic_class] += 1
        changes.append(
            DiffFieldChange(
                field=field,
                change_class=change_class,
                impact=impact,
                semantic_class=semantic_class,
                left=left_value,
                right=right_value,
            )
        )

    summary = (
        "No semantic changes detected."
        if not changed_fields
        else (
            f"Changed fields ({len(changed_fields)}): {', '.join(changed_fields)} | "
            f"breaking={semantic_counts['breaking']}, "
            f"additive={semantic_counts['additive']}, "
            f"editorial={semantic_counts['editorial']}"
        )
    )
    return DiffReport(
        report_id=f"diff_{stable_text_hash(left_ref + right_ref)[:16]}",
        left_ref=left_ref,
        right_ref=right_ref,
        summary=summary,
        changes=changes,
    )
