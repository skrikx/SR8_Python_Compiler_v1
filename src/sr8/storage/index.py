from __future__ import annotations

import json

from sr8.models.artifact_record import ArtifactRecord
from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.intent_artifact import IntentArtifact
from sr8.storage.workspace import SR8Workspace


def _read_catalog(workspace: SR8Workspace) -> dict[str, object]:
    payload = json.loads(workspace.catalog_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        msg = "Catalog payload is invalid."
        raise ValueError(msg)
    payload.setdefault("records", [])
    return payload


def load_records(workspace: SR8Workspace) -> list[ArtifactRecord]:
    payload = _read_catalog(workspace)
    raw_records = payload.get("records", [])
    if not isinstance(raw_records, list):
        msg = "Catalog records must be a list."
        raise ValueError(msg)
    return [ArtifactRecord.model_validate(item) for item in raw_records]


def save_records(workspace: SR8Workspace, records: list[ArtifactRecord]) -> None:
    payload = {"records": [record.model_dump(mode="json") for record in records]}
    workspace.catalog_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _next_record_id(records: list[ArtifactRecord], kind: str) -> str:
    prefix = "art" if kind == "canonical" else "drv"
    numbers = [
        int(record.record_id.split("_")[1])
        for record in records
        if record.record_id.startswith(f"{prefix}_") and record.record_id.split("_")[1].isdigit()
    ]
    next_number = max(numbers, default=0) + 1
    return f"{prefix}_{next_number:03d}"


def add_record(workspace: SR8Workspace, record: ArtifactRecord) -> ArtifactRecord:
    records = load_records(workspace)
    assigned = record.model_copy(
        update={"record_id": _next_record_id(records, record.artifact_kind)}
    )
    records.append(assigned)
    save_records(workspace, records)
    return assigned


def query_records(
    workspace: SR8Workspace,
    kind: str | None = None,
    profile: str | None = None,
) -> list[ArtifactRecord]:
    records = load_records(workspace)
    filtered = records
    if kind is not None:
        filtered = [record for record in filtered if record.artifact_kind == kind]
    if profile is not None:
        filtered = [record for record in filtered if record.profile == profile]
    return filtered


def resolve_record(workspace: SR8Workspace, identifier: str) -> ArtifactRecord:
    for record in load_records(workspace):
        if identifier in {record.record_id, record.artifact_id}:
            return record
    msg = f"Record '{identifier}' not found in catalog."
    raise ValueError(msg)


def rebuild_index(workspace: SR8Workspace) -> list[ArtifactRecord]:
    workspace.initialize()
    rebuilt: list[ArtifactRecord] = []

    for path in sorted(workspace.canonical_dir.glob("*.json")):
        if path.name == "latest.json":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        artifact = IntentArtifact.model_validate(payload)
        rebuilt.append(
            ArtifactRecord(
                record_id="",
                artifact_id=artifact.artifact_id,
                artifact_kind="canonical",
                profile=artifact.profile,
                target_class=artifact.target_class,
                transform_target=None,
                source_hash=artifact.source.source_hash,
                created_at=artifact.created_at,
                file_path=str(path),
                parent_artifact_id=None,
                readiness_status=artifact.validation.readiness_status,
            )
        )

    for path in sorted(workspace.derivative_dir.glob("*.json")):
        if path.name == "latest.json":
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        derivative = DerivativeArtifact.model_validate(payload)
        rebuilt.append(
            ArtifactRecord(
                record_id="",
                artifact_id=derivative.derivative_id,
                artifact_kind="derivative",
                profile=derivative.profile,
                target_class=derivative.profile,
                transform_target=derivative.transform_target,
                source_hash=derivative.lineage.parent_source_hash,
                created_at=derivative.created_at,
                file_path=str(path),
                parent_artifact_id=derivative.parent_artifact_id,
                readiness_status="derived",
            )
        )

    records: list[ArtifactRecord] = []
    for record in rebuilt:
        records.append(
            record.model_copy(update={"record_id": _next_record_id(records, record.artifact_kind)})
        )
    save_records(workspace, records)
    return records
