from __future__ import annotations

from sr8.lint.report import build_lint_report
from sr8.lint.rules import evaluate_rules
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.lint_report import LintReport


def lint_artifact(artifact: IntentArtifact, artifact_ref: str) -> LintReport:
    findings = evaluate_rules(artifact)
    return build_lint_report(artifact_ref=artifact_ref, findings=findings)
