from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from sr8.extract.core import extract_dimensions as extract_dimensions_core
from sr8.extract.signals import ExtractedDimensions
from sr8.ingest.loaders import load_source as ingest_load_source
from sr8.models.base import utc_now
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
from sr8.validate.engine import validate_artifact

from .types import CompilationResult, CompileConfig

SourceInput = str | Path | Mapping[str, object]


def load_source(source: SourceInput, source_type: SourceType | None = None) -> SourceIntent:
    return ingest_load_source(source=source, source_type=source_type)


def normalize_source(source_intent: SourceIntent) -> SourceIntent:
    return normalize_source_core(source_intent)


def extract_dimensions(normalized_source: SourceIntent) -> ExtractedDimensions:
    source_text = normalized_source.normalized_content or normalized_source.raw_content
    return extract_dimensions_core(source_text)


def assemble_artifact(
    source_intent: SourceIntent,
    extracted_dimensions: ExtractedDimensions,
    config: CompileConfig | None = None,
) -> IntentArtifact:
    active_config = config or CompileConfig()

    artifact_id = build_artifact_id(
        source_hash=source_intent.source_hash,
        artifact_version=active_config.artifact_version,
        compiler_version=active_config.compiler_version,
    )

    compile_run_id = build_compile_run_id(source_intent.source_hash)
    lineage = Lineage(
        compile_run_id=compile_run_id,
        pipeline_version=active_config.compiler_version,
        source_hash=source_intent.source_hash,
        steps=[
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
    }
    if active_config.include_raw_source:
        metadata["raw_content"] = source_intent.raw_content

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


def compile_intent(
    source: SourceInput,
    source_type: SourceType | None = None,
    config: CompileConfig | None = None,
) -> CompilationResult:
    loaded = load_source(source=source, source_type=source_type)
    normalized = normalize_source(loaded)
    extracted = extract_dimensions(normalized)
    active_config = config or CompileConfig()
    assembled = assemble_artifact(normalized, extracted, config=active_config)
    profiled = apply_profile_overlay(assembled, active_config.profile)
    validation_report = validate_artifact(profiled, profile_name=active_config.profile)
    artifact = profiled.model_copy(update={"validation": validation_report})
    receipt = CompilationReceipt(
        receipt_id=build_receipt_id(artifact.artifact_id, normalized.source_hash),
        artifact_id=artifact.artifact_id,
        source_hash=normalized.source_hash,
        status="accepted",
        notes=["Compiled with deterministic rule-first pipeline."],
    )
    return CompilationResult(
        artifact=artifact,
        receipt=receipt,
        normalized_source=normalized,
        extracted_dimensions=extracted,
    )
