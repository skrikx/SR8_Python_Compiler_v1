from __future__ import annotations

import json
from pathlib import Path

from sr8.models.artifact_record import ArtifactRecord
from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.intent_artifact import IntentArtifact
from sr8.storage.atomic import atomic_write_text
from sr8.storage.index import add_record
from sr8.storage.paths import ensure_unique_path
from sr8.storage.workspace import SR8Workspace


def save_canonical_artifact(
    workspace: SR8Workspace,
    artifact: IntentArtifact,
) -> tuple[Path, Path, ArtifactRecord]:
    workspace.initialize()
    payload = json.dumps(artifact.model_dump(mode="json"), indent=2, sort_keys=True)

    artifact_path = ensure_unique_path(workspace.canonical_dir / f"{artifact.artifact_id}.json")
    latest_path = workspace.canonical_dir / "latest.json"
    atomic_write_text(artifact_path, payload, workspace.tmp_dir)
    atomic_write_text(latest_path, payload, workspace.tmp_dir)

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
    markdown_path = ensure_unique_path(workspace.derivative_dir / f"{derivative.derivative_id}.md")
    latest_json = workspace.derivative_dir / "latest.json"
    latest_markdown = workspace.derivative_dir / "latest.md"

    atomic_write_text(json_path, payload, workspace.tmp_dir)
    atomic_write_text(markdown_path, derivative.content, workspace.tmp_dir)
    atomic_write_text(latest_json, payload, workspace.tmp_dir)
    atomic_write_text(latest_markdown, derivative.content, workspace.tmp_dir)

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
    return json_path, markdown_path, latest_json, indexed
