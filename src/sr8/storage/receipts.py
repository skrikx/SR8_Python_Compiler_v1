from __future__ import annotations

import json
from pathlib import Path

from sr8.compiler.types import CompilationResult
from sr8.models.compilation_receipt import CompilationReceiptRecord
from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.transform_receipt import TransformReceiptRecord
from sr8.storage.paths import ensure_unique_path
from sr8.storage.workspace import SR8Workspace
from sr8.utils.hash import stable_text_hash


def _receipt_id(prefix: str, payload: str) -> str:
    return f"{prefix}_{stable_text_hash(payload)[:20]}"


def write_compilation_receipt(
    workspace: SR8Workspace,
    result: CompilationResult,
    output_path: str,
) -> tuple[CompilationReceiptRecord, Path]:
    artifact = result.artifact
    report = artifact.validation
    receipt = CompilationReceiptRecord(
        receipt_id=_receipt_id("crpt", f"{artifact.artifact_id}:{output_path}"),
        artifact_id=artifact.artifact_id,
        compiler_version=artifact.compiler_version,
        source_hash=artifact.source.source_hash,
        profile=artifact.profile,
        target_class=artifact.target_class,
        extracted_dimensions_summary={
            "objective": result.extracted_dimensions.objective,
            "scope_count": len(result.extracted_dimensions.scope),
            "constraints_count": len(result.extracted_dimensions.constraints),
            "success_criteria_count": len(result.extracted_dimensions.success_criteria),
        },
        validation_summary=report.summary,
        warnings=[warning.message for warning in report.warnings],
        output_path=output_path,
    )
    payload = json.dumps(receipt.model_dump(mode="json"), indent=2, sort_keys=True)
    receipt_path = ensure_unique_path(workspace.compile_receipts_dir / f"{receipt.receipt_id}.json")
    receipt_path.write_text(payload, encoding="utf-8")
    return receipt, receipt_path


def write_transform_receipt(
    workspace: SR8Workspace,
    derivative: DerivativeArtifact,
    output_path: str,
) -> tuple[TransformReceiptRecord, Path]:
    renderer_version = str(derivative.metadata.get("renderer_version", "unknown"))
    receipt = TransformReceiptRecord(
        receipt_id=_receipt_id("trpt", f"{derivative.derivative_id}:{output_path}"),
        parent_artifact_id=derivative.parent_artifact_id,
        derivative_id=derivative.derivative_id,
        transform_target=derivative.transform_target,
        profile=derivative.profile,
        renderer_version=renderer_version,
        output_path=output_path,
    )
    payload = json.dumps(receipt.model_dump(mode="json"), indent=2, sort_keys=True)
    receipt_path = ensure_unique_path(
        workspace.transform_receipts_dir / f"{receipt.receipt_id}.json"
    )
    receipt_path.write_text(payload, encoding="utf-8")
    return receipt, receipt_path
