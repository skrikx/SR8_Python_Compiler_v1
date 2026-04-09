from __future__ import annotations

from sr8.models.diff_report import DiffReport


def render_diff_report(report: DiffReport) -> str:
    lines = [
        f"Diff Report: {report.report_id}",
        f"Left: {report.left_ref}",
        f"Right: {report.right_ref}",
        f"Summary: {report.summary}",
    ]
    for change in report.changes:
        if change.change_class == "unchanged":
            continue
        lines.append(
            f"- {change.field}: {change.change_class} "
            f"(impact={change.impact}, semantic={change.semantic_class})"
        )
    return "\n".join(lines)
