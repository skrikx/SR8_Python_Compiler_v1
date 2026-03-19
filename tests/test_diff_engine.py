from sr8.diff.engine import semantic_diff
from sr8.diff.render import render_diff_report
from sr8.io.exporters import load_artifact


def test_diff_engine_reports_semantic_changes() -> None:
    left = load_artifact("tests/fixtures/diff/base_artifact.json")
    right = load_artifact("tests/fixtures/diff/changed_artifact.json")
    report = semantic_diff(left, right, "base", "changed")

    assert report.left_ref == "base"
    assert report.right_ref == "changed"
    assert any(
        change.field == "scope" and change.change_class == "modified"
        for change in report.changes
    )
    assert any(
        change.field == "constraints" and change.impact == "high"
        for change in report.changes
    )


def test_diff_render_outputs_readable_summary() -> None:
    left = load_artifact("tests/fixtures/diff/base_artifact.json")
    right = load_artifact("tests/fixtures/diff/changed_artifact.json")
    report = semantic_diff(left, right, "base", "changed")
    rendered = render_diff_report(report)
    assert "Diff Report:" in rendered
    assert "Summary:" in rendered
    assert "scope" in rendered
