from sr8.compiler import CompileConfig, compile_intent


def test_research_brief_profile_passes_with_evidence_expectations() -> None:
    source = (
        "Objective: Investigate onboarding drop-off\n"
        "Scope:\n"
        "- Compare cohorts\n"
        "Constraints:\n"
        "- One week limit\n"
        "Success Criteria:\n"
        "- Evidence links included\n"
        "Output Contract:\n"
        "- Findings report\n"
    )
    result = compile_intent(source=source, config=CompileConfig(profile="research_brief"))
    assert result.artifact.profile == "research_brief"
    assert result.artifact.validation.readiness_status == "pass"
