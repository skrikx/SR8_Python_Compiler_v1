from sr8.compiler import CompileConfig, compile_intent


def test_regression_profile_plan_remains_enforced() -> None:
    source = (
        "Objective: deliver project plan\n"
        "Scope:\n- Phase 1 baseline\n- Phase 2 rollout\n"
        "Dependencies:\n- qa team\n"
        "Success Criteria:\n- plan approved\n"
        "Output Contract:\n- plan markdown\n"
    )
    result = compile_intent(source, config=CompileConfig(profile="plan"))
    assert result.artifact.profile == "plan"
    assert result.artifact.validation.readiness_status == "pass"


def test_regression_profile_procedure_enforcement_remains() -> None:
    source = (
        "Objective: run ops procedure\n"
        "Authority Context:\n- ops owner\n"
        "Scope:\n- Step 1 check system\n- Step 2 remediate\n"
        "Constraints:\n- fallback to previous version\n"
        "Success Criteria:\n- escalate to owner on high severity\n"
        "Output Contract:\n- procedure markdown\n"
    )
    result = compile_intent(source, config=CompileConfig(profile="procedure"))
    assert result.artifact.profile == "procedure"
    assert result.artifact.validation.readiness_status == "pass"
