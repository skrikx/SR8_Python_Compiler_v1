from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from sr8.models.intent_artifact import IntentArtifact
from sr8.models.validation import ValidationIssue

ProfileSeverity = Literal["error", "warning"]
ProfileCheck = Callable[[IntentArtifact], bool]


@dataclass(frozen=True)
class ProfileRule:
    code: str
    message: str
    path: str
    severity: ProfileSeverity
    check: ProfileCheck


@dataclass(frozen=True)
class ProfileDefinition:
    name: str
    target_class: str
    required_rules: tuple[ProfileRule, ...]
    warning_rules: tuple[ProfileRule, ...] = ()

    def apply(self, artifact: IntentArtifact) -> IntentArtifact:
        if self.name == "generic":
            target_class = artifact.target_class.strip() or self.target_class
        else:
            target_class = self.target_class
        return artifact.model_copy(update={"profile": self.name, "target_class": target_class})

    def validate(
        self,
        artifact: IntentArtifact,
    ) -> tuple[list[ValidationIssue], list[ValidationIssue]]:
        errors = _evaluate_rules(artifact, self.required_rules)
        warnings = _evaluate_rules(artifact, self.warning_rules)
        return errors, warnings


def _evaluate_rules(
    artifact: IntentArtifact,
    rules: tuple[ProfileRule, ...],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for rule in rules:
        if rule.check(artifact):
            continue
        issues.append(
            ValidationIssue(
                code=rule.code,
                message=rule.message,
                severity="error" if rule.severity == "error" else "warning",
                path=rule.path,
            )
        )
    return issues
