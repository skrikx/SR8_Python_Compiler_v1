from __future__ import annotations

from typing import Literal

DiffClass = Literal["added", "removed", "modified", "unchanged"]
ImpactLevel = Literal["low", "medium", "high"]

SEMANTIC_FIELDS: tuple[str, ...] = (
    "profile",
    "objective",
    "scope",
    "exclusions",
    "constraints",
    "assumptions",
    "dependencies",
    "success_criteria",
    "output_contract",
    "governance_flags",
    "validation.readiness_status",
    "target_class",
)

HIGH_IMPACT_FIELDS = {"scope", "exclusions", "constraints", "success_criteria", "output_contract"}
MEDIUM_IMPACT_FIELDS = {
    "objective",
    "dependencies",
    "assumptions",
    "profile",
    "target_class",
    "validation.readiness_status",
}
