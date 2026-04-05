from sr8.compiler import CompileConfig, compile_intent
from sr8.transform.engine import transform_artifact


def test_code_task_graph_profile_sets_target_class() -> None:
    artifact = compile_intent(
        (
            "Objective: Ship code graph\n"
            "Scope:\n- Build parser\n- Build scheduler\n"
            "Dependencies:\n- Python\n"
        ),
        config=CompileConfig(profile="code_task_graph"),
    ).artifact
    assert artifact.profile == "code_task_graph"
    assert artifact.target_class == "code_task_graph"


def test_code_task_graph_supports_prompt_pack_transform() -> None:
    artifact = compile_intent(
        (
            "Objective: Ship code graph\n"
            "Scope:\n- Build parser\n- Build scheduler\n"
            "Dependencies:\n- Python\n"
        ),
        config=CompileConfig(profile="code_task_graph"),
    ).artifact

    derivative = transform_artifact(artifact, "markdown_prompt_pack").derivative

    assert derivative.transform_target == "markdown_prompt_pack"
