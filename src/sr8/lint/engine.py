from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from sr8.extract.trace import coerce_extraction_trace
from sr8.lint.report import build_lint_report
from sr8.lint.rules import evaluate_rules
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.lint_finding import LintFinding
from sr8.models.lint_report import LintReport

TRUST_FINDING_FIELDS = (
    "authority_context",
    "dependencies",
    "assumptions",
    "success_criteria",
    "output_contract",
    "context_package",
)


def _build_trust_findings(artifact: IntentArtifact) -> list[LintFinding]:
    raw_trace = cast(Mapping[str, object] | None, artifact.metadata.get("extraction_trace"))
    trace = coerce_extraction_trace(raw_trace)
    if trace is None:
        return []

    findings: list[LintFinding] = []
    for signal in trace.confidence:
        if signal.field_name not in TRUST_FINDING_FIELDS:
            continue
        if signal.status not in {"weak", "contradictory"}:
            continue
        findings.append(
            LintFinding(
                rule_id=f"L-TRUST-{signal.field_name.upper()}",
                severity="error" if signal.status == "contradictory" else "warn",
                message=f"Extraction trust for {signal.field_name} is {signal.status}",
                artifact_field=signal.field_name,
                suggested_fix="Strengthen the source directive or review the artifact manually.",
            )
        )

    if artifact.governance_flags.requires_human_review:
        findings.append(
            LintFinding(
                rule_id="L-TRUST-GOVERNANCE",
                severity="warn",
                message="Governance flags request human review",
                artifact_field="governance_flags.requires_human_review",
                suggested_fix="Review ambiguous or incomplete inputs before downstream use.",
            )
        )
    return findings


def lint_artifact(artifact: IntentArtifact, artifact_ref: str) -> LintReport:
    findings = evaluate_rules(artifact) + _build_trust_findings(artifact)
    return build_lint_report(artifact_ref=artifact_ref, findings=findings)
