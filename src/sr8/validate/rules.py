from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from sr8.models.intent_artifact import IntentArtifact
from sr8.models.validation import ValidationIssue

RuleSeverity = Literal["error", "warning"]
RuleCheck = Callable[[IntentArtifact], bool]


@dataclass(frozen=True)
class Rule:
    code: str
    message: str
    path: str
    severity: RuleSeverity
    check: RuleCheck


def _has_text(value: str) -> bool:
    return value.strip() != ""


def _has_any(values: list[str]) -> bool:
    return any(item.strip() for item in values)


def _contradiction_between_scope_and_exclusions(artifact: IntentArtifact) -> bool:
    scope_set = {item.strip().lower() for item in artifact.scope if item.strip()}
    exclusion_set = {item.strip().lower() for item in artifact.exclusions if item.strip()}
    return bool(scope_set & exclusion_set)


CANONICAL_RULES: tuple[Rule, ...] = (
    Rule(
        code="VAL-CAN-001",
        message="artifact_id must be present",
        path="artifact_id",
        severity="error",
        check=lambda artifact: _has_text(artifact.artifact_id),
    ),
    Rule(
        code="VAL-CAN-002",
        message="source hash must be present",
        path="source.source_hash",
        severity="error",
        check=lambda artifact: _has_text(artifact.source.source_hash),
    ),
    Rule(
        code="VAL-CAN-003",
        message="objective is empty",
        path="objective",
        severity="error",
        check=lambda artifact: _has_text(artifact.objective),
    ),
    Rule(
        code="VAL-CAN-004",
        message="scope is empty",
        path="scope",
        severity="warning",
        check=lambda artifact: _has_any(artifact.scope),
    ),
    Rule(
        code="VAL-CAN-005",
        message="success_criteria is empty",
        path="success_criteria",
        severity="warning",
        check=lambda artifact: _has_any(artifact.success_criteria),
    ),
    Rule(
        code="VAL-CAN-006",
        message="output_contract is empty",
        path="output_contract",
        severity="warning",
        check=lambda artifact: _has_any(artifact.output_contract),
    ),
    Rule(
        code="VAL-CAN-007",
        message="scope and exclusions conflict on at least one item",
        path="scope",
        severity="error",
        check=lambda artifact: not _contradiction_between_scope_and_exclusions(artifact),
    ),
)


def execute_rules(
    artifact: IntentArtifact,
    rules: tuple[Rule, ...],
) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
    errors: list[ValidationIssue] = []
    warnings: list[ValidationIssue] = []
    for rule in rules:
        if rule.check(artifact):
            continue
        issue = ValidationIssue(
            code=rule.code,
            message=rule.message,
            severity="error" if rule.severity == "error" else "warning",
            path=rule.path,
        )
        if rule.severity == "error":
            errors.append(issue)
        else:
            warnings.append(issue)
    return errors, warnings
