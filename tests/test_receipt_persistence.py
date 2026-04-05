from pathlib import Path

from sr8.compiler import CompileConfig, compile_intent
from sr8.storage.receipts import write_compilation_receipt, write_transform_receipt
from sr8.storage.save import save_canonical_artifact, save_derivative_artifact
from sr8.storage.workspace import init_workspace
from sr8.transform.engine import transform_artifact


def test_receipts_persist_for_compile_and_transform(tmp_path: Path) -> None:
    workspace = init_workspace(tmp_path / ".sr8")
    result = compile_intent(
        source="tests/fixtures/product_prd.md",
        config=CompileConfig(profile="prd"),
    )
    artifact_path, _, _ = save_canonical_artifact(workspace, result.artifact)
    compile_receipt, compile_receipt_path = write_compilation_receipt(
        workspace,
        result=result,
        output_path=str(artifact_path),
    )
    assert compile_receipt_path.exists()
    assert compile_receipt.artifact_id == result.artifact.artifact_id
    assert compile_receipt.source_hash == result.artifact.source.source_hash
    assert compile_receipt.lineage_summary["source_hash"] == result.artifact.source.source_hash
    assert "status_counts" in compile_receipt.extraction_trust_summary

    transform_result = transform_artifact(result.artifact, target="markdown_prd")
    derivative_json_path, _, _, _ = save_derivative_artifact(workspace, transform_result.derivative)
    transform_receipt, transform_receipt_path = write_transform_receipt(
        workspace,
        derivative=transform_result.derivative,
        output_path=str(derivative_json_path),
    )
    assert transform_receipt_path.exists()
    assert transform_receipt.parent_artifact_id == result.artifact.artifact_id
