from sr8.compiler import CompileConfig, compile_intent


def test_plan_profile_passes_with_ordered_scope_and_dependencies() -> None:
    source = (
        "Objective: Execute release plan\n"
        "Scope:\n"
        "- Phase 1. baseline\n"
        "- Phase 2. refactor\n"
        "Dependencies:\n"
        "- QA team\n"
        "Success Criteria:\n"
        "- Release candidate approved\n"
        "Output Contract:\n"
        "- Plan markdown\n"
    )
    result = compile_intent(source=source, config=CompileConfig(profile="plan"))
    assert result.artifact.profile == "plan"
    assert result.artifact.validation.readiness_status == "pass"
