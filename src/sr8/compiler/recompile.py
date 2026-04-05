from __future__ import annotations

from sr8.models.base import utc_now
from sr8.models.compile_config import CompileConfig
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.lineage import LineageStep
from sr8.profiles.registry import apply_profile_overlay
from sr8.utils.ids import build_artifact_id, build_compile_run_id
from sr8.validate.engine import validate_artifact


def recompile_artifact(
    artifact: IntentArtifact,
    profile: str | None = None,
    config: CompileConfig | None = None,
) -> IntentArtifact:
    active_config = config or CompileConfig()
    effective_profile = profile or active_config.profile or artifact.profile
    rebuilt_id = build_artifact_id(
        source_hash=artifact.source.source_hash,
        artifact_version=active_config.artifact_version,
        compiler_version=active_config.compiler_version,
    )
    lineage = artifact.lineage.model_copy(
        update={
            "compile_run_id": build_compile_run_id(artifact.source.source_hash),
            "pipeline_version": active_config.compiler_version,
            "source_hash": artifact.source.source_hash,
            "parent_artifact_ids": [*artifact.lineage.parent_artifact_ids, artifact.artifact_id],
            "steps": [
                *artifact.lineage.steps,
                LineageStep(
                    stage="recompile",
                    detail=f"Recompiled from artifact_id={artifact.artifact_id}",
                    occurred_at=utc_now(),
                ),
            ],
        }
    )
    rebuilt = artifact.model_copy(
        update={
            "artifact_id": rebuilt_id,
            "artifact_version": active_config.artifact_version,
            "compiler_version": active_config.compiler_version,
            "created_at": utc_now(),
            "lineage": lineage,
            "metadata": artifact.metadata | {"recompiled_from": artifact.artifact_id},
        }
    )
    profiled = apply_profile_overlay(rebuilt, effective_profile)
    report = validate_artifact(profiled, profile_name=effective_profile)
    return profiled.model_copy(update={"validation": report})
