from sr8.compiler import CompileConfig, compile_intent
from sr8.storage.catalog import list_catalog, show_catalog_record
from sr8.storage.save import save_canonical_artifact, save_derivative_artifact
from sr8.storage.workspace import init_workspace
from sr8.transform.engine import transform_artifact


def test_index_catalog_tracks_canonical_and_derivative_records(tmp_path) -> None:
    workspace = init_workspace(tmp_path / ".sr8")
    compiled = compile_intent("tests/fixtures/product_prd.md", config=CompileConfig(profile="prd"))
    _, _, canonical_record = save_canonical_artifact(workspace, compiled.artifact)

    transformed = transform_artifact(compiled.artifact, target="markdown_prd")
    _, _, _, derivative_record = save_derivative_artifact(workspace, transformed.derivative)

    all_records = list_catalog(workspace)
    canonical_records = list_catalog(workspace, kind="canonical")
    shown = show_catalog_record(workspace, canonical_record.record_id)

    assert len(all_records) == 2
    assert len(canonical_records) == 1
    assert shown.artifact_id == compiled.artifact.artifact_id
    assert derivative_record.parent_artifact_id == compiled.artifact.artifact_id
