from sr8.compiler import CompileConfig, compile_intent


def test_generic_profile_overlay_defaults_target_class() -> None:
    result = compile_intent(
        source="tests/fixtures/founder_generic.md",
        config=CompileConfig(profile="generic"),
    )

    artifact = result.artifact
    assert artifact.profile == "generic"
    assert artifact.target_class in {"generic", "compiler_core"}
    assert artifact.validation.readiness_status in {"pass", "warn"}
