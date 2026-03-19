from __future__ import annotations

from sr8.models.lint_finding import LintFinding
from sr8.models.lint_report import LintReport
from sr8.utils.hash import stable_text_hash


def build_lint_report(artifact_ref: str, findings: list[LintFinding]) -> LintReport:
    severities = {finding.severity for finding in findings}
    if "error" in severities:
        status = "fail"
    elif "warn" in severities:
        status = "warn"
    else:
        status = "pass"
    summary = f"Lint {status}: {len(findings)} finding(s)."
    return LintReport(
        report_id=f"lint_{stable_text_hash(artifact_ref)[:16]}",
        artifact_ref=artifact_ref,
        status=status,
        summary=summary,
        findings=findings,
    )
