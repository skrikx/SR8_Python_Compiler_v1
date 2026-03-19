from sr8.io.exporters import load_artifact
from sr8.lint.engine import lint_artifact


def test_lint_engine_status_fail_for_weak_artifact() -> None:
    artifact = load_artifact("tests/fixtures/lint/weak_artifact.json")
    report = lint_artifact(artifact, artifact_ref="weak")
    assert report.status == "fail"
    assert len(report.findings) >= 1


def test_lint_engine_status_pass_for_strong_artifact() -> None:
    artifact = load_artifact("tests/fixtures/lint/strong_artifact.json")
    report = lint_artifact(artifact, artifact_ref="strong")
    assert report.status == "pass"
    assert report.findings == []
