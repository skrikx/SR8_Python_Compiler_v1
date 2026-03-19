from sr8.compiler import CompileConfig, compile_intent


def test_procedure_profile_passes_with_steps_fallback_and_escalation() -> None:
    source = (
        "Objective: Run incident triage procedure\n"
        "Authority Context:\n"
        "- operations owner\n"
        "Scope:\n"
        "- Step 1. Collect logs\n"
        "- Step 2. Validate alerts\n"
        "Constraints:\n"
        "- Fallback to previous stable release\n"
        "Success Criteria:\n"
        "- Escalate to owner when severity is critical\n"
        "Output Contract:\n"
        "- Procedure markdown\n"
    )
    result = compile_intent(source=source, config=CompileConfig(profile="procedure"))
    assert result.artifact.profile == "procedure"
    assert result.artifact.validation.readiness_status == "pass"
