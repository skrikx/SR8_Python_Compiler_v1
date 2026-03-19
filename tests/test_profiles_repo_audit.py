from sr8.compiler import CompileConfig, compile_intent


def test_repo_audit_profile_enforcement_passes_for_repo_fixture() -> None:
    result = compile_intent(
        source="tests/fixtures/repo_audit_request.md",
        config=CompileConfig(profile="repo_audit"),
    )

    artifact = result.artifact
    assert artifact.profile == "repo_audit"
    assert artifact.target_class == "repo_audit"
    assert artifact.validation.readiness_status == "pass"
