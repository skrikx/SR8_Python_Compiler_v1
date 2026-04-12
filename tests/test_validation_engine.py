from sr8.compiler import CompileConfig, compile_intent


def test_validation_pass_status_for_complete_generic_fixture() -> None:
    result = compile_intent(
        source="tests/fixtures/founder_generic.md",
        config=CompileConfig(profile="generic"),
    )
    assert result.artifact.validation.readiness_status == "pass"
    assert result.artifact.validation.errors == []


def test_validation_fail_status_for_intake_required_request() -> None:
    result = compile_intent(
        source="tests/fixtures/ambiguous_request.txt",
        config=CompileConfig(profile="generic"),
    )
    assert result.artifact.validation.readiness_status == "fail"
    assert any(issue.code == "VAL-ROUTE-004" for issue in result.artifact.validation.errors)


def test_validation_fail_for_scope_exclusion_contradiction() -> None:
    source = (
        "Objective: Evaluate repo quality\n"
        "Scope:\n- Security checks\n"
        "Exclusions:\n- Security checks\n"
        "Success Criteria:\n- Report generated\n"
        "Output Contract:\n- audit report\n"
    )
    result = compile_intent(source=source, config=CompileConfig(profile="repo_audit"))
    assert result.artifact.validation.readiness_status == "fail"
    assert any(issue.code == "VAL-CAN-007" for issue in result.artifact.validation.errors)
