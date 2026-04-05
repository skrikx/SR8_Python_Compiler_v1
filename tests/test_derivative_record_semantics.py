from sr8.compiler import CompileConfig, compile_intent
from sr8.storage.catalog import list_catalog
from sr8.storage.index import rebuild_index
from sr8.storage.save import save_canonical_artifact, save_derivative_artifact
from sr8.storage.workspace import init_workspace
from sr8.transform.engine import transform_artifact


def test_derivative_records_preserve_derivative_semantics(tmp_path) -> None:
    workspace = init_workspace(tmp_path / ".sr8")
    compiled = compile_intent(
        "Objective: Derivative semantics\nScope:\n- one\n",
        config=CompileConfig(profile="prd", extraction_adapter="rule_based"),
    )
    save_canonical_artifact(workspace, compiled.artifact)

    transformed = transform_artifact(compiled.artifact, target="markdown_prd")
    _, _, _, record = save_derivative_artifact(workspace, transformed.derivative)

    assert record.artifact_kind == "derivative"
    assert record.target_class is None
    assert record.transform_target == "markdown_prd"
    assert record.parent_artifact_id == compiled.artifact.artifact_id

    rebuilt_records = rebuild_index(workspace)
    rebuilt_derivative = next(
        item for item in rebuilt_records if item.artifact_kind == "derivative"
    )

    assert rebuilt_derivative.target_class is None
    assert rebuilt_derivative.transform_target == "markdown_prd"
    assert len(list_catalog(workspace)) == 2
