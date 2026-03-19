from sr8.compiler import CompileConfig, compile_intent
from sr8.storage.load import load_derivative
from sr8.storage.save import save_canonical_artifact, save_derivative_artifact
from sr8.storage.workspace import init_workspace
from sr8.transform.engine import transform_artifact


def test_lineage_integrity_persists_between_canonical_and_derivative(tmp_path) -> None:
    workspace = init_workspace(tmp_path / ".sr8")
    compiled = compile_intent(
        source="tests/fixtures/repo_audit_request.md",
        config=CompileConfig(profile="repo_audit"),
    )
    _, _, canonical_record = save_canonical_artifact(workspace, compiled.artifact)
    transformed = transform_artifact(compiled.artifact, target="markdown_research_brief")
    derivative_path, _, _, derivative_record = save_derivative_artifact(
        workspace,
        transformed.derivative,
    )

    loaded_derivative = load_derivative(derivative_path)
    assert derivative_record.parent_artifact_id == canonical_record.artifact_id
    assert loaded_derivative.parent_artifact_id == canonical_record.artifact_id
    assert loaded_derivative.lineage.parent_source_hash == compiled.artifact.source.source_hash
