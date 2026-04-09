from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from sr8.diff.types import (
    HIGH_IMPACT_FIELDS,
    MEDIUM_IMPACT_FIELDS,
    DiffClass,
    ImpactLevel,
)


def _is_empty(value: object | None) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return len(value) == 0
    if isinstance(value, Mapping):
        return len(value) == 0
    return False


def normalize_semantic_value(value: object | None) -> object | None:
    if isinstance(value, list):
        normalized_list = [str(item).strip() for item in value if str(item).strip()]
        return sorted(normalized_list)
    if isinstance(value, Mapping):
        normalized_map = {
            str(key): normalize_semantic_value(sub_value)
            for key, sub_value in value.items()
        }
        return dict(sorted(normalized_map.items()))
    if isinstance(value, str):
        return value.strip()
    return value


def classify_change(left: object | None, right: object | None) -> DiffClass:
    normalized_left = normalize_semantic_value(left)
    normalized_right = normalize_semantic_value(right)
    if normalized_left == normalized_right:
        return "unchanged"
    if _is_empty(normalized_left) and not _is_empty(normalized_right):
        return "added"
    if not _is_empty(normalized_left) and _is_empty(normalized_right):
        return "removed"
    return "modified"


def classify_impact(field: str, change_class: DiffClass) -> ImpactLevel:
    if change_class == "unchanged":
        return "low"
    if field in HIGH_IMPACT_FIELDS:
        return "high"
    if field in MEDIUM_IMPACT_FIELDS:
        return "medium"
    return "low"


def classify_semantic_change(
    field: str,
    change_class: DiffClass,
    left: object | None,
    right: object | None,
) -> Literal["breaking", "additive", "editorial", "unchanged"]:
    if change_class == "unchanged":
        return "unchanged"
    if field == "validation.readiness_status":
        ordering = {"pass": 0, "warn": 1, "fail": 2}
        left_rank = ordering.get(str(left), 0)
        right_rank = ordering.get(str(right), 0)
        if right_rank > left_rank:
            return "breaking"
        if right_rank < left_rank:
            return "additive"
        return "editorial"
    if field == "governance_flags":
        left_text = str(normalize_semantic_value(left)).lower()
        right_text = str(normalize_semantic_value(right)).lower()
        if "true" in right_text and "true" not in left_text:
            return "breaking"
        if "true" in left_text and "true" not in right_text:
            return "additive"
        return "editorial"
    if change_class == "added":
        return "additive"
    if change_class == "removed":
        return "breaking"
    if field in HIGH_IMPACT_FIELDS or field in MEDIUM_IMPACT_FIELDS:
        return "breaking"
    return "editorial"
