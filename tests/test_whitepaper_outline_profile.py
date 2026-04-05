from sr8.compiler import CompileConfig, compile_intent
from sr8.transform.engine import transform_artifact


def test_whitepaper_outline_profile_sets_target_class() -> None:
    artifact = compile_intent(
        "Objective: Publish architecture whitepaper\nScope:\n- Intro\n- Design\n",
        config=CompileConfig(profile="whitepaper_outline"),
    ).artifact
    assert artifact.profile == "whitepaper_outline"
    assert artifact.target_class == "whitepaper_outline"


def test_whitepaper_outline_supports_plan_transform() -> None:
    artifact = compile_intent(
        "Objective: Publish architecture whitepaper\nScope:\n- Intro\n- Design\n",
        config=CompileConfig(profile="whitepaper_outline"),
    ).artifact

    derivative = transform_artifact(artifact, "markdown_plan").derivative

    assert derivative.transform_target == "markdown_plan"
