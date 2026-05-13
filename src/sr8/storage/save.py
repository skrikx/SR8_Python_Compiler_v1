from __future__ import annotations

import json
from pathlib import Path

from sr8.models.artifact_record import ArtifactRecord
from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.intent_artifact import IntentArtifact
from sr8.storage.atomic import atomic_write_text, file_lock
from sr8.storage.index import add_record
from sr8.storage.paths import ensure_unique_path
from sr8.storage.workspace import SR8Workspace


def _write_latest_alias(workspace: SR8Workspace, path: Path, content: str) -> None:
    lock_path = workspace.index_dir / f"{path.name}.lock"
    with file_lock(lock_path):
        atomic_write_text(path, content, workspace.tmp_dir)


def save_canonical_artifact(
    workspace: SR8Workspace,
    artifact: IntentArtifact,
) -> tuple[Path, Path, ArtifactRecord]:
    workspace.initialize()
    payload = json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True)

    artifact_path = ensure_unique_path(workspace.canonical_dir / f"{artifact.artifact_id}.json")
    latest_path = workspace.canonical_dir / "latest.json"
    atomic_write_text(artifact_path, payload, workspace.tmp_dir)
    _write_latest_alias(workspace, latest_path, payload)

    indexed = add_record(
        workspace,
        ArtifactRecord(
            record_id="",
            artifact_id=artifact.artifact_id,
            artifact_kind="canonical",
            profile=artifact.profile,
            target_class=artifact.target_class,
            transform_target=None,
            source_hash=artifact.source.source_hash,
            created_at=artifact.created_at,
            file_path=str(artifact_path),
            parent_artifact_id=None,
            readiness_status=artifact.validation.readiness_status,
        ),
    )
    return artifact_path, latest_path, indexed


def save_derivative_artifact(
    workspace: SR8Workspace,
    derivative: DerivativeArtifact,
) -> tuple[Path, Path, Path, ArtifactRecord]:
    workspace.initialize()
    payload = json.dumps(derivative.model_dump(mode="json"), indent=2, sort_keys=True)

    json_path = ensure_unique_path(workspace.derivative_dir / f"{derivative.derivative_id}.json")
    output_format = str(derivative.metadata.get("output_format") or "markdown")
    extension = ".xml" if output_format == "xml" else ".md"
    native_path = ensure_unique_path(
        workspace.derivative_dir / f"{derivative.derivative_id}{extension}"
    )
    latest_json = workspace.derivative_dir / "latest.json"
    latest_native = workspace.derivative_dir / f"latest{extension}"

    atomic_write_text(json_path, payload, workspace.tmp_dir)
    atomic_write_text(native_path, derivative.content, workspace.tmp_dir)
    _write_latest_alias(workspace, latest_json, payload)
    _write_latest_alias(workspace, latest_native, derivative.content)

    indexed = add_record(
        workspace,
        ArtifactRecord(
            record_id="",
            artifact_id=derivative.derivative_id,
            artifact_kind="derivative",
            profile=derivative.profile,
            target_class=None,
            transform_target=derivative.transform_target,
            source_hash=derivative.lineage.parent_source_hash,
            created_at=derivative.created_at,
            file_path=str(json_path),
            parent_artifact_id=derivative.parent_artifact_id,
            readiness_status="derived",
        ),
    )
    return json_path, native_path, latest_json, indexed
