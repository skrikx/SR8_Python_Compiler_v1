from __future__ import annotations

from collections.abc import Mapping

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
