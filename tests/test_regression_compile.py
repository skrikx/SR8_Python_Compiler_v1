from sr8.compiler import CompileConfig, compile_intent


def test_regression_compile_shape_stable_for_prd_fixture() -> None:
    result = compile_intent(
        source="tests/fixtures/product_prd.md",
        config=CompileConfig(profile="prd"),
    )
    artifact = result.artifact
    assert artifact.artifact_id.startswith("art_")
    assert artifact.profile == "prd"
    assert artifact.validation.readiness_status in {"pass", "warn", "fail"}
    assert isinstance(artifact.scope, list)
    assert isinstance(artifact.constraints, list)
