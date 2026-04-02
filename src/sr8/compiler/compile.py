from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from sr8.extract.adapters.registry import get_extraction_adapter
from sr8.extract.core import extract_dimensions as extract_dimensions_core
from sr8.extract.signals import ExtractedDimensions
from sr8.extract.trace import summarize_extraction_trace
from sr8.ingest.loaders import load_source as ingest_load_source
from sr8.models.base import utc_now
from sr8.models.compile_config import CompileConfig
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

from .recompile import recompile_artifact
from .types import CompilationResult

SourceInput = str | Path | Mapping[str, object] | IntentArtifact


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
        receipt = CompilationReceipt(
            receipt_id=build_receipt_id(
                compiled_artifact.artifact_id,
                compiled_artifact.source.source_hash,
            ),
            artifact_id=compiled_artifact.artifact_id,
            source_hash=compiled_artifact.source.source_hash,
            status="accepted",
            notes=["Recompiled from in-memory canonical artifact source."],
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
    if source_type is None and isinstance(source, (str, Path)):
        candidate = Path(source)
        candidate_exists = False
        try:
            candidate_exists = candidate.exists()
        except OSError:
            candidate_exists = False
        if candidate_exists and candidate.suffix.lower() in {".json", ".yaml", ".yml"}:
            from sr8.io.exporters import load_artifact

            compiled_artifact = recompile_artifact(
                load_artifact(candidate),
                profile=active_config.profile if config is not None else None,
                config=active_config,
            )
            receipt = CompilationReceipt(
                receipt_id=build_receipt_id(
                    compiled_artifact.artifact_id,
                    compiled_artifact.source.source_hash,
                ),
                artifact_id=compiled_artifact.artifact_id,
                source_hash=compiled_artifact.source.source_hash,
                status="accepted",
                notes=["Recompiled from canonical artifact source."],
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
    loaded = load_source(source=source, source_type=source_type)
    normalized = normalize_source(loaded)
    adapter = get_extraction_adapter(active_config.extraction_adapter)
    extracted, extraction_trace = adapter.extract(
        normalized.normalized_content or normalized.raw_content,
        config=active_config,
    )
    assembled = assemble_artifact(normalized, extracted, config=active_config)
    assembled = assembled.model_copy(
        update={
            "metadata": assembled.metadata
            | {
                "extraction_trace": extraction_trace.model_dump(mode="json"),
                "extraction_trust_summary": summarize_extraction_trace(extraction_trace),
                "provider_assist": extraction_trace.metadata,
            }
        }
    )
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
