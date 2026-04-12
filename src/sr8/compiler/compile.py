from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Literal, cast

from pydantic import ValidationError

from sr8.compiler.planner import (
    IMPORTANT_FIELDS,
    MATERIAL_DERIVED_FIELDS,
    SEMANTIC_IMPORTANT_DERIVED_MIN,
    STRUCTURE_FIELDS,
    build_compile_preview,
    build_recovery_summary,
    merge_source_values,
)
from sr8.compiler.semantic import expand_dimensions
from sr8.extract.adapters.registry import get_extraction_adapter
from sr8.extract.confidence import build_confidence_signals
from sr8.extract.core import extract_dimensions as extract_dimensions_core
from sr8.extract.signals import ExtractedDimensions, GovernanceSignals
from sr8.extract.trace import build_extraction_trace, summarize_extraction_trace
from sr8.ingest.loaders import load_source as ingest_load_source
from sr8.io.exporters import load_artifact
from sr8.models.base import utc_now
from sr8.models.compile_config import CompileConfig
from sr8.models.extraction_trace import ExtractionTrace
from sr8.models.intent_artifact import ArtifactSource, GovernanceFlags, IntentArtifact
from sr8.models.lineage import Lineage, LineageStep
from sr8.models.receipts import CompilationReceipt
from sr8.models.source_intent import SourceIntent, SourceType
from sr8.models.validation import ValidationReport
from sr8.normalize.clean import normalize_source as normalize_source_core
from sr8.profiles.registry import apply_profile_overlay
from sr8.utils.ids import (
    build_artifact_id,
    build_compile_run_id,
    build_receipt_id,
)
from sr8.utils.paths import resolve_trusted_local_path
from sr8.validate.engine import validate_artifact

from .errors import SR8CompileError
from .recompile import recompile_artifact
from .types import CompilationResult

SourceInput = str | Path | Mapping[str, object] | IntentArtifact
ReceiptStatus = Literal["accepted", "rejected"]
CompileKind = Literal[
    "semantic_compile",
    "canonicalize_structured",
    "needs_intake",
]


def load_source(source: SourceInput, source_type: SourceType | None = None) -> SourceIntent:
    if isinstance(source, IntentArtifact):
        msg = "load_source does not accept IntentArtifact instances. Use compile_intent instead."
        raise TypeError(msg)
    return ingest_load_source(source=source, source_type=source_type)


def normalize_source(source_intent: SourceIntent) -> SourceIntent:
    return normalize_source_core(source_intent)


def extract_dimensions(normalized_source: SourceIntent) -> ExtractedDimensions:
    source_text = normalized_source.normalized_content or normalized_source.raw_content
    return extract_dimensions_core(source_text)


def summarize_extracted_dimensions(extracted: ExtractedDimensions) -> dict[str, object]:
    return {
        "objective": extracted.objective,
        "scope_count": len(extracted.scope),
        "constraints_count": len(extracted.constraints),
        "dependencies_count": len(extracted.dependencies),
        "success_criteria_count": len(extracted.success_criteria),
    }


def assemble_artifact(
    source_intent: SourceIntent,
    extracted_dimensions: ExtractedDimensions,
    config: CompileConfig | None = None,
    *,
    lineage_steps: list[LineageStep] | None = None,
    metadata_updates: Mapping[str, object] | None = None,
) -> IntentArtifact:
    active_config = config or CompileConfig()

    artifact_id = build_artifact_id(
        source_hash=source_intent.source_hash,
        artifact_version=active_config.artifact_version,
        compiler_version=active_config.compiler_version,
    )

    compile_run_id = build_compile_run_id(source_intent.source_hash, stage="compile")
    lineage = Lineage(
        compile_run_id=compile_run_id,
        pipeline_version=active_config.compiler_version,
        source_hash=source_intent.source_hash,
        steps=lineage_steps
        or [
            LineageStep(stage="ingest", detail=f"Loaded source_type={source_intent.source_type}"),
            LineageStep(stage="normalize", detail="Normalized whitespace and wrappers"),
            LineageStep(stage="extract", detail="Applied rule-first extraction"),
            LineageStep(stage="assemble", detail=f"Assembled artifact_id={artifact_id}"),
        ],
    )

    metadata: dict[str, object] = {
        "source_metadata": source_intent.metadata,
        "normalized_char_count": len(source_intent.normalized_content),
        "pipeline_mode": "rule-first",
        "normalized_source_hash": source_intent.metadata.get("normalized_source_hash"),
    }
    if active_config.include_raw_source:
        metadata["raw_content"] = source_intent.raw_content
    if metadata_updates is not None:
        metadata |= dict(metadata_updates)

    return IntentArtifact(
        artifact_id=artifact_id,
        artifact_version=active_config.artifact_version,
        compiler_version=active_config.compiler_version,
        profile=active_config.profile,
        created_at=utc_now(),
        source=ArtifactSource(
            source_id=source_intent.source_id,
            source_type=source_intent.source_type,
            source_hash=source_intent.source_hash,
            origin=source_intent.origin,
        ),
        objective=extracted_dimensions.objective,
        scope=extracted_dimensions.scope,
        exclusions=extracted_dimensions.exclusions,
        constraints=extracted_dimensions.constraints,
        context_package=extracted_dimensions.context_package,
        target_class=extracted_dimensions.target_class,
        authority_context=extracted_dimensions.authority_context,
        dependencies=extracted_dimensions.dependencies,
        assumptions=extracted_dimensions.assumptions,
        success_criteria=extracted_dimensions.success_criteria,
        output_contract=extracted_dimensions.output_contract,
        governance_flags=GovernanceFlags(
            ambiguous=extracted_dimensions.governance_flags.ambiguous,
            incomplete=extracted_dimensions.governance_flags.incomplete,
            requires_human_review=extracted_dimensions.governance_flags.requires_human_review,
        ),
        validation=ValidationReport(
            report_id=f"val_{source_intent.source_hash[:16]}",
            readiness_status="warn",
            summary="Validation pending.",
        ),
        lineage=lineage,
        metadata=metadata,
    )


def _assert_assembly_invariants(
    artifact: IntentArtifact,
    source_intent: SourceIntent,
) -> None:
    if artifact.source.source_hash != source_intent.source_hash:
        raise SR8CompileError(
            code="artifact_assembly_invariant_failed",
            message="Artifact source hash diverged from the ingested source hash.",
            details={
                "artifact_source_hash": artifact.source.source_hash,
                "source_hash": source_intent.source_hash,
            },
        )
    if artifact.lineage.source_hash != source_intent.source_hash:
        raise SR8CompileError(
            code="lineage_source_hash_mismatch",
            message="Artifact lineage source hash diverged from the ingested source hash.",
            details={
                "lineage_source_hash": artifact.lineage.source_hash,
                "source_hash": source_intent.source_hash,
            },
        )


def _field_has_value(value: object) -> bool:
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, list):
        return any(str(item).strip() for item in value)
    return value is not None


def _dimensions_field_has_value(dimensions: ExtractedDimensions, field_name: str) -> bool:
    return _field_has_value(getattr(dimensions, field_name))


def _artifact_field_has_value(artifact: IntentArtifact, field_name: str) -> bool:
    return _field_has_value(getattr(artifact, field_name))


def _sorted_fields(values: set[str] | list[str]) -> list[str]:
    return sorted(str(item) for item in values)


def _metadata_list(metadata: Mapping[str, object], key: str) -> list[str]:
    value = metadata.get(key)
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _metadata_int(metadata: Mapping[str, object], key: str) -> int:
    value = metadata.get(key)
    return value if isinstance(value, int) else 0


def _assist_route(
    trace_adapter: str,
    trace_metadata: Mapping[str, object],
    config: CompileConfig,
) -> str:
    metadata_route = trace_metadata.get("assist_extract_route")
    if isinstance(metadata_route, str) and metadata_route:
        return metadata_route
    if trace_adapter.startswith("structured_"):
        return "not_used"
    if config.extraction_adapter == "model_assisted":
        return "model_assisted"
    return "rule_based"


def _build_truth_summary(
    *,
    compile_kind: str,
    source_structure_kind: str,
    source_supplied_field_count: int,
    compiler_derived_fields: list[str],
    unresolved_fields: list[str],
) -> str:
    source_label = source_structure_kind.replace("_", " ")
    if compile_kind == "semantic_compile":
        derived = ", ".join(
            field for field in compiler_derived_fields if field in MATERIAL_DERIVED_FIELDS
        )
        if not derived:
            derived = "additional governed structure"
        return (
            f"Semantic compile expanded {source_label} input and derived {derived} "
            f"from compiler-owned lowering."
        )
    if compile_kind == "canonicalize_structured":
        return (
            f"Canonicalized {source_label} input with {source_supplied_field_count} "
            "source-supplied field(s) and no material semantic expansion."
        )
    missing = ", ".join(field for field in unresolved_fields if field in IMPORTANT_FIELDS)
    if not missing:
        missing = "objective, scope, constraints, success_criteria, output_contract"
    return (
        f"Needs intake: {source_label} input remained under-specified for truthful compile. "
        f"Unresolved fields: {missing}."
    )


def _build_compile_metadata(
    artifact: IntentArtifact,
    *,
    preview_source_fields: set[str],
    source_structure_kind: str,
    compile_kind: str,
    semantic_transform_applied: bool,
    assist_route: str,
    weak_signal_hits: list[str],
) -> dict[str, object]:
    source_supplied_fields = _sorted_fields(preview_source_fields)
    compiler_derived_fields = _sorted_fields(
        {
            field_name
            for field_name in STRUCTURE_FIELDS
            if field_name not in preview_source_fields
            and _artifact_field_has_value(artifact, field_name)
        }
    )
    unresolved_fields = _sorted_fields(
        [
            field_name
            for field_name in STRUCTURE_FIELDS
            if not _artifact_field_has_value(artifact, field_name)
        ]
    )
    intake_route = (
        "needs_intake"
        if compile_kind == "needs_intake"
        else "semantic_recovery"
        if semantic_transform_applied
        and len(preview_source_fields & set(IMPORTANT_FIELDS)) < len(IMPORTANT_FIELDS)
        else "not_required"
    )
    source_supplied_field_count = len(source_supplied_fields)
    compile_truth_summary = _build_truth_summary(
        compile_kind=compile_kind,
        source_structure_kind=source_structure_kind,
        source_supplied_field_count=source_supplied_field_count,
        compiler_derived_fields=compiler_derived_fields,
        unresolved_fields=unresolved_fields,
    )
    recovery_summary = build_recovery_summary(
        compile_kind=compile_kind,
        source_supplied_fields=preview_source_fields,
        compiler_derived_fields=compiler_derived_fields,
        unresolved_fields=unresolved_fields,
        weak_signal_hits=weak_signal_hits,
    )
    return {
        "compile_kind": compile_kind,
        "semantic_transform_applied": semantic_transform_applied,
        "source_structure_kind": source_structure_kind,
        "source_supplied_fields": source_supplied_fields,
        "compiler_derived_fields": compiler_derived_fields,
        "unresolved_fields": unresolved_fields,
        "derived_field_count": len(compiler_derived_fields),
        "source_supplied_field_count": source_supplied_field_count,
        "copied_field_count": source_supplied_field_count,
        "assist_route": assist_route,
        "intake_route": intake_route,
        "compile_truth_summary": compile_truth_summary,
        "weak_intent_recovery": recovery_summary,
    }


def _build_lineage_steps(
    source_intent: SourceIntent,
    *,
    source_structure_kind: str,
    compile_kind: str,
    reason: str,
    used_extraction: bool,
    extraction_adapter_name: str,
    semantic_transform_applied: bool,
) -> list[LineageStep]:
    steps = [
        LineageStep(stage="ingest", detail=f"Loaded source_type={source_intent.source_type}"),
        LineageStep(stage="normalize", detail="Normalized whitespace and wrappers"),
        LineageStep(
            stage="detect_surface",
            detail=f"Detected source_structure_kind={source_structure_kind}",
        ),
        LineageStep(
            stage="assess_intent_strength",
            detail="Assessed compile route candidate based on source coverage and specificity.",
        ),
        LineageStep(
            stage="route_selected",
            detail=f"compile_kind={compile_kind}; reason={reason}",
        ),
    ]
    if used_extraction:
        steps.append(
            LineageStep(
                stage="extract",
                detail=f"Applied extraction adapter={extraction_adapter_name}",
            )
        )
    if semantic_transform_applied:
        steps.append(
            LineageStep(
                stage="semantic_expand",
                detail="Derived missing intent dimensions from the source.",
            )
        )
    steps.extend(
        [
            LineageStep(
                stage="lower_to_canonical",
                detail="Lowered compile result into canonical fields",
            ),
            LineageStep(stage="validate", detail="Validated readiness and compile truth"),
        ]
    )
    return steps


def _structured_trace(
    dimensions: ExtractedDimensions,
    *,
    source_structure_kind: str,
) -> tuple[str, Mapping[str, object], ExtractionTrace]:
    adapter_name = (
        "structured_payload"
        if source_structure_kind.startswith("structured_")
        else "structured_outline"
    )
    metadata: dict[str, object] = {
        "assist_extract_status": "not_used",
        "assist_extract_route": "not_used",
        "provider": None,
        "model": None,
    }
    trace = build_extraction_trace(
        adapter_name=adapter_name,
        confidence=build_confidence_signals(dimensions, inferred_fields=set()),
        metadata=metadata,
    )
    return adapter_name, metadata, trace


def _receipt_compile_kind(metadata: Mapping[str, object]) -> CompileKind:
    value = metadata.get("compile_kind")
    if value in {"semantic_compile", "canonicalize_structured", "needs_intake"}:
        return cast(CompileKind, value)
    return "canonicalize_structured"


def _build_receipt_from_artifact(
    artifact: IntentArtifact,
    *,
    source_hash: str,
    status: ReceiptStatus,
    notes: list[str],
) -> CompilationReceipt:
    metadata = artifact.metadata
    return CompilationReceipt(
        receipt_id=build_receipt_id(artifact.artifact_id, source_hash),
        artifact_id=artifact.artifact_id,
        source_hash=source_hash,
        compile_run_id=artifact.lineage.compile_run_id,
        status=status,
        notes=notes,
        parent_artifact_ids=artifact.lineage.parent_artifact_ids,
        compile_kind=_receipt_compile_kind(metadata),
        semantic_transform_applied=bool(metadata.get("semantic_transform_applied", False)),
        source_structure_kind=str(metadata.get("source_structure_kind", "canonical_artifact")),
        source_supplied_fields=_metadata_list(metadata, "source_supplied_fields"),
        compiler_derived_fields=_metadata_list(metadata, "compiler_derived_fields"),
        unresolved_fields=_metadata_list(metadata, "unresolved_fields"),
        derived_field_count=_metadata_int(metadata, "derived_field_count"),
        source_supplied_field_count=_metadata_int(metadata, "source_supplied_field_count"),
        assist_route=str(metadata.get("assist_route", "not_used")),
        intake_route=str(metadata.get("intake_route", "not_required")),
        compile_truth_summary=str(metadata.get("compile_truth_summary", "")),
    )


def _recompile_result(
    compiled_artifact: IntentArtifact,
    *,
    note: str,
) -> CompilationResult:
    receipt = _build_receipt_from_artifact(
        compiled_artifact,
        source_hash=compiled_artifact.source.source_hash,
        status="accepted",
        notes=[note],
    )
    fallback_source = SourceIntent(
        source_id=compiled_artifact.source.source_id,
        source_type=compiled_artifact.source.source_type,
        raw_content=str(compiled_artifact.metadata.get("raw_content", "")),
        normalized_content=str(compiled_artifact.metadata.get("raw_content", "")),
        source_hash=compiled_artifact.source.source_hash,
        origin=compiled_artifact.source.origin,
        metadata={},
    )
    return CompilationResult(
        artifact=compiled_artifact,
        receipt=receipt,
        normalized_source=fallback_source,
        extracted_dimensions=ExtractedDimensions(),
    )


def _try_recompile_artifact_path(
    candidate: Path,
    *,
    active_config: CompileConfig,
) -> CompilationResult | None:
    try:
        source_artifact = load_artifact(candidate)
    except (ValidationError, ValueError):
        return None
    compiled_artifact = recompile_artifact(
        source_artifact,
        profile=active_config.profile if active_config is not None else None,
        config=active_config,
    )
    return _recompile_result(
        compiled_artifact,
        note="Recompiled from canonical artifact source.",
    )


def compile_intent(
    source: SourceInput,
    source_type: SourceType | None = None,
    config: CompileConfig | None = None,
) -> CompilationResult:
    active_config = config or CompileConfig()
    if isinstance(source, IntentArtifact):
        compiled_artifact = recompile_artifact(
            source,
            profile=active_config.profile if config is not None else None,
            config=active_config,
        )
        return _recompile_result(
            compiled_artifact,
            note="Recompiled from in-memory canonical artifact source.",
        )

    if source_type is None and isinstance(source, (str, Path)):
        try:
            candidate = resolve_trusted_local_path(source, must_exist=True)
        except (FileNotFoundError, OSError, ValueError):
            candidate = None
        if candidate is not None and candidate.suffix.lower() in {".json", ".yaml", ".yml"}:
            recompile_result = _try_recompile_artifact_path(
                candidate,
                active_config=active_config,
            )
            if recompile_result is not None:
                return recompile_result

    loaded = load_source(source=source, source_type=source_type)
    normalized = normalize_source(loaded)
    preview = build_compile_preview(normalized)
    source_text = normalized.normalized_content or normalized.raw_content

    used_extraction = False
    if preview.compile_kind == "canonicalize_structured":
        base_dimensions = merge_source_values(ExtractedDimensions(), preview.source_values)
        extraction_adapter_name, trace_metadata, extraction_trace = _structured_trace(
            base_dimensions,
            source_structure_kind=preview.source_structure_kind,
        )
    else:
        adapter = get_extraction_adapter(active_config.extraction_adapter)
        extracted, extraction_trace = adapter.extract(
            source_text,
            config=active_config,
        )
        used_extraction = True
        extraction_adapter_name = extraction_trace.adapter_name
        trace_metadata = extraction_trace.metadata
        base_dimensions = merge_source_values(extracted, preview.source_values)

    initial_compiler_derived_fields = {
        field_name
        for field_name in STRUCTURE_FIELDS
        if field_name not in preview.source_supplied_fields
        and _dimensions_field_has_value(base_dimensions, field_name)
    }

    compile_kind = preview.compile_kind
    candidate_dimensions = base_dimensions
    semantic_candidate_fields = set(initial_compiler_derived_fields)
    if preview.compile_kind == "semantic_compile":
        expansion = expand_dimensions(source_text, base_dimensions, preview)
        candidate_dimensions = expansion.dimensions
        semantic_candidate_fields |= expansion.compiler_derived_fields
        material_derived_fields = semantic_candidate_fields & set(MATERIAL_DERIVED_FIELDS)
        if len(material_derived_fields) < SEMANTIC_IMPORTANT_DERIVED_MIN:
            compile_kind = "needs_intake"

    semantic_transform_applied = (
        compile_kind == "semantic_compile"
        and len(semantic_candidate_fields & set(MATERIAL_DERIVED_FIELDS))
        >= SEMANTIC_IMPORTANT_DERIVED_MIN
    )
    selected_dimensions = (
        candidate_dimensions
        if semantic_transform_applied or compile_kind == "canonicalize_structured"
        else base_dimensions
    )
    base_governance = selected_dimensions.governance_flags
    compiled_dimensions = selected_dimensions.model_copy(
        update={
            "governance_flags": GovernanceSignals(
                ambiguous=base_governance.ambiguous or not selected_dimensions.objective.strip(),
                incomplete=compile_kind == "needs_intake",
                requires_human_review=compile_kind == "needs_intake",
            )
        }
    )

    trust_summary = summarize_extraction_trace(extraction_trace)
    assist_route = _assist_route(
        extraction_adapter_name,
        trace_metadata,
        active_config,
    )
    lineage_steps = _build_lineage_steps(
        normalized,
        source_structure_kind=preview.source_structure_kind,
        compile_kind=compile_kind,
        reason=preview.reason,
        used_extraction=used_extraction,
        extraction_adapter_name=extraction_adapter_name,
        semantic_transform_applied=semantic_transform_applied,
    )
    pipeline_mode = (
        "semantic_compile"
        if semantic_transform_applied
        else "canonicalize_structured"
        if compile_kind == "canonicalize_structured"
        else "needs_intake"
    )
    assembled = assemble_artifact(
        normalized,
        compiled_dimensions,
        config=active_config,
        lineage_steps=lineage_steps,
        metadata_updates={
            "extraction_trace": extraction_trace.model_dump(mode="json"),
            "extraction_trust_summary": trust_summary,
            "provider_assist": extraction_trace.metadata,
            "pipeline_mode": pipeline_mode,
            "extraction_adapter": extraction_adapter_name,
        },
    )
    _assert_assembly_invariants(assembled, normalized)
    profiled = apply_profile_overlay(assembled, active_config.profile)
    compile_metadata = _build_compile_metadata(
        profiled,
        preview_source_fields=preview.source_supplied_fields,
        source_structure_kind=preview.source_structure_kind,
        compile_kind=compile_kind,
        semantic_transform_applied=semantic_transform_applied,
        assist_route=assist_route,
        weak_signal_hits=preview.weak_signal_hits,
    )
    profiled = profiled.model_copy(update={"metadata": profiled.metadata | compile_metadata})
    validation_report = validate_artifact(profiled, profile_name=active_config.profile)
    artifact = profiled.model_copy(update={"validation": validation_report})

    receipt_status: ReceiptStatus = (
        "rejected" if compile_kind == "needs_intake" else "accepted"
    )
    notes = [str(artifact.metadata["compile_truth_summary"])]
    if semantic_transform_applied:
        notes.append("Semantic transform applied.")
    elif compile_kind == "canonicalize_structured":
        notes.append("Structured canonicalization preserved source-supplied structure.")
    else:
        notes.append("Compilation stopped at explicit intake-required route.")
    receipt = _build_receipt_from_artifact(
        artifact,
        source_hash=normalized.source_hash,
        status=receipt_status,
        notes=notes,
    )
    return CompilationResult(
        artifact=artifact,
        receipt=receipt,
        normalized_source=normalized,
        extracted_dimensions=compiled_dimensions,
    )
