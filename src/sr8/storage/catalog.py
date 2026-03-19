from __future__ import annotations

from sr8.models.artifact_record import ArtifactRecord
from sr8.storage.index import query_records, resolve_record
from sr8.storage.workspace import SR8Workspace


def list_catalog(
    workspace: SR8Workspace,
    kind: str | None = None,
    profile: str | None = None,
) -> list[ArtifactRecord]:
    return query_records(workspace=workspace, kind=kind, profile=profile)


def show_catalog_record(workspace: SR8Workspace, identifier: str) -> ArtifactRecord:
    return resolve_record(workspace=workspace, identifier=identifier)
