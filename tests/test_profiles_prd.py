from sr8.compiler import CompileConfig, compile_intent


def test_prd_profile_enforcement_passes_for_prd_fixture() -> None:
    result = compile_intent(
        source="tests/fixtures/product_prd.md",
        config=CompileConfig(profile="prd"),
    )

    artifact = result.artifact
    assert artifact.profile == "prd"
    assert artifact.target_class == "prd"
    assert artifact.validation.readiness_status == "pass"
