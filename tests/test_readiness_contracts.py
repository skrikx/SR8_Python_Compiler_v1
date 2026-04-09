from sr8.compiler import compile_intent
from sr8.io.exporters import load_artifact
from sr8.validate.engine import validate_artifact


def test_readiness_pass_for_strong_fixture() -> None:
    artifact = load_artifact("tests/fixtures/lint/strong_artifact.json")
    report = validate_artifact(artifact, profile_name=artifact.profile)

    assert report.readiness_status == "pass"


def test_readiness_warn_for_recoverable_weak_intent() -> None:
    artifact = compile_intent("Objective: Build tool\nScope:\n- parser\n").artifact

    assert artifact.validation.readiness_status == "warn"


def test_readiness_fail_for_invalid_artifact() -> None:
    artifact = load_artifact("tests/fixtures/lint/weak_artifact.json")
    report = validate_artifact(artifact, profile_name=artifact.profile)

    assert report.readiness_status == "fail"
