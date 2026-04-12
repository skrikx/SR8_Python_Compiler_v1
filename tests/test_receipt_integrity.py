from pathlib import Path

from sr8.compiler import compile_intent
from sr8.storage.receipts import write_compilation_receipt, write_transform_receipt
from sr8.storage.save import save_canonical_artifact, save_derivative_artifact
from sr8.storage.workspace import init_workspace
from sr8.transform.engine import transform_artifact


def test_receipts_preserve_lineage_and_recovery_fields(tmp_path: Path) -> None:
    workspace = init_workspace(tmp_path / ".sr8")
    result = compile_intent("Objective: Build tool\nScope:\n- parser\n")

    artifact_path, _, _ = save_canonical_artifact(workspace, result.artifact)
    compile_receipt, _ = write_compilation_receipt(
        workspace,
        result=result,
        output_path=str(artifact_path),
    )

    assert compile_receipt.compile_run_id == result.artifact.lineage.compile_run_id
    assert compile_receipt.lineage_summary["source_hash"] == result.artifact.source.source_hash
    assert compile_receipt.compile_kind == result.artifact.metadata["compile_kind"]
    assert (
        compile_receipt.derived_field_count
        == result.artifact.metadata["derived_field_count"]
    )
    assert compile_receipt.recovery_summary["intake_required"] is False

    derivative = transform_artifact(result.artifact, target="markdown_plan").derivative
    derivative_path, _, _, _ = save_derivative_artifact(workspace, derivative)
    transform_receipt, _ = write_transform_receipt(
        workspace,
        derivative=derivative,
        output_path=str(derivative_path),
    )

    assert transform_receipt.parent_source_hash == result.artifact.source.source_hash
    assert transform_receipt.parent_compile_run_id == result.artifact.lineage.compile_run_id
