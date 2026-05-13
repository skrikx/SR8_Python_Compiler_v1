from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from sr8.compiler.types import CompilationResult
from sr8.extract.trace import summarize_extraction_trace
from sr8.models.compilation_receipt import CompilationReceiptRecord
from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.transform_receipt import TransformReceiptRecord
from sr8.storage.paths import ensure_unique_path
from sr8.storage.workspace import SR8Workspace
from sr8.utils.hash import stable_text_hash


def _receipt_id(prefix: str, payload: str) -> str:
    return f"{prefix}_{stable_text_hash(payload)[:20]}"


def _metadata_list(metadata: Mapping[str, object], key: str) -> list[str]:
    value = metadata.get(key)
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _metadata_int(metadata: Mapping[str, object], key: str) -> int:
    value = metadata.get(key)
    return value if isinstance(value, int) else 0


def _metadata_bool(metadata: Mapping[str, object], key: str) -> bool:
    value = metadata.get(key)
    return value if isinstance(value, bool) else False


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
        compile_run_id=artifact.lineage.compile_run_id,
        profile=artifact.profile,
        target_class=artifact.target_class,
        extracted_dimensions_summary={
            "objective": result.extracted_dimensions.objective,
            "scope_count": len(result.extracted_dimensions.scope),
            "constraints_count": len(result.extracted_dimensions.constraints),
            "success_criteria_count": len(result.extracted_dimensions.success_criteria),
        },
        extraction_trust_summary=summarize_extraction_trace(
            cast(Mapping[str, object] | None, artifact.metadata.get("extraction_trace"))
        ),
        recovery_summary=cast(
            dict[str, object],
            artifact.metadata.get("weak_intent_recovery", {}),
        ),
        lineage_summary={
            "compile_run_id": artifact.lineage.compile_run_id,
            "source_hash": artifact.lineage.source_hash,
            "parent_compile_run_id": artifact.lineage.parent_compile_run_id,
            "parent_artifact_count": len(artifact.lineage.parent_artifact_ids),
            "steps": [step.stage for step in artifact.lineage.steps],
        },
        validation_summary=report.summary,
        warnings=[warning.message for warning in report.warnings],
        compile_kind=str(artifact.metadata.get("compile_kind", "canonicalize_structured")),
        semantic_transform_applied=bool(
            artifact.metadata.get("semantic_transform_applied", False)
        ),
        source_structure_kind=str(artifact.metadata.get("source_structure_kind", "raw_text")),
        source_supplied_fields=_metadata_list(artifact.metadata, "source_supplied_fields"),
        compiler_derived_fields=_metadata_list(artifact.metadata, "compiler_derived_fields"),
        unresolved_fields=_metadata_list(artifact.metadata, "unresolved_fields"),
        derived_field_count=_metadata_int(artifact.metadata, "derived_field_count"),
        source_supplied_field_count=_metadata_int(
            artifact.metadata,
            "source_supplied_field_count",
        ),
        assist_route=str(artifact.metadata.get("assist_route", "not_used")),
        intake_route=str(artifact.metadata.get("intake_route", "not_required")),
        compile_truth_summary=str(artifact.metadata.get("compile_truth_summary", "")),
        assist_mode=str(
            artifact.metadata.get("assist_mode", artifact.metadata.get("compile_mode", "auto"))
        ),
        llm_used=_metadata_bool(artifact.metadata, "llm_used"),
        provider=cast(str | None, artifact.metadata.get("provider")),
        model=cast(str | None, artifact.metadata.get("model")),
        adapter=str(
            artifact.metadata.get(
                "adapter",
                artifact.metadata.get("extraction_adapter", "rule_based"),
            )
        ),
        prompt_template_id=cast(str | None, artifact.metadata.get("prompt_template_id")),
        prompt_hash=cast(str | None, artifact.metadata.get("prompt_hash")),
        raw_response_hash=cast(str | None, artifact.metadata.get("raw_response_hash")),
        parsed_response_hash=cast(str | None, artifact.metadata.get("parsed_response_hash")),
        repair_attempts=_metadata_int(artifact.metadata, "repair_attempts"),
        schema_validation_status=str(artifact.metadata.get("schema_validation_status", "pass")),
        fallback_used=_metadata_bool(artifact.metadata, "fallback_used"),
        confidence=cast(float | None, artifact.metadata.get("confidence")),
        compile_target=cast(str | None, artifact.metadata.get("compile_target")),
        compile_target_validation=cast(
            dict[str, object] | None,
            artifact.metadata.get("compile_target_validation"),
        ),
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
        parent_source_hash=derivative.lineage.parent_source_hash,
        parent_compile_run_id=derivative.lineage.parent_compile_run_id,
        renderer_version=renderer_version,
        output_path=output_path,
    )
    payload = json.dumps(receipt.model_dump(mode="json"), indent=2, sort_keys=True)
    receipt_path = ensure_unique_path(
        workspace.transform_receipts_dir / f"{receipt.receipt_id}.json"
    )
    receipt_path.write_text(payload, encoding="utf-8")
    return receipt, receipt_path
