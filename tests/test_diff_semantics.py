from sr8.diff.engine import semantic_diff
from sr8.io.exporters import load_artifact


def test_diff_classifies_breaking_changes_for_high_impact_fields() -> None:
    left = load_artifact("tests/fixtures/diff/base_artifact.json")
    right = load_artifact("tests/fixtures/diff/changed_artifact.json")

    report = semantic_diff(left, right, "base", "changed")
    change_by_field = {change.field: change for change in report.changes}

    assert change_by_field["scope"].semantic_class == "breaking"
    assert change_by_field["constraints"].semantic_class == "breaking"
    assert "breaking=" in report.summary


def test_diff_classifies_readiness_improvement_as_additive() -> None:
    left = load_artifact("tests/fixtures/lint/strong_artifact.json")
    right = left.model_copy(
        update={
            "validation": left.validation.model_copy(
                update={"readiness_status": "pass", "summary": "Validation pass."}
            )
        }
    )
    left_warn = left.model_copy(
        update={
            "validation": left.validation.model_copy(
                update={"readiness_status": "warn", "summary": "Validation warn."}
            )
        }
    )

    report = semantic_diff(left_warn, right, "warn", "pass")
    change = next(
        change
        for change in report.changes
        if change.field == "validation.readiness_status"
    )

    assert change.semantic_class == "additive"
