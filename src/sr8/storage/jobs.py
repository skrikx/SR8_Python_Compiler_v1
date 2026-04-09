from __future__ import annotations

import json
from pathlib import Path

from sr8.models.async_job import AsyncJobRecord
from sr8.models.base import utc_now
from sr8.storage.atomic import atomic_write_text, file_lock
from sr8.storage.workspace import SR8Workspace
from sr8.utils.hash import stable_text_hash


def _job_path(workspace: SR8Workspace, job_id: str) -> Path:
    return workspace.jobs_dir / f"{job_id}.json"


def _load_idempotency_index(workspace: SR8Workspace) -> dict[str, dict[str, str]]:
    payload = json.loads(workspace.idempotency_index_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        msg = "Idempotency index payload is invalid."
        raise ValueError(msg)
    output: dict[str, dict[str, str]] = {}
    for key, value in payload.items():
        if isinstance(key, str) and isinstance(value, dict):
            output[key] = {
                str(inner_key): str(inner_value)
                for inner_key, inner_value in value.items()
            }
    return output


def _save_idempotency_index(workspace: SR8Workspace, index: dict[str, dict[str, str]]) -> None:
    atomic_write_text(
        workspace.idempotency_index_path,
        json.dumps(index, indent=2, sort_keys=True),
        workspace.tmp_dir,
    )


def _read_job_unlocked(workspace: SR8Workspace, job_id: str) -> AsyncJobRecord:
    job_path = _job_path(workspace, job_id)
    if not job_path.exists():
        msg = f"Job '{job_id}' not found."
        raise ValueError(msg)
    payload = json.loads(job_path.read_text(encoding="utf-8"))
    return AsyncJobRecord.model_validate(payload)


def _write_job_unlocked(workspace: SR8Workspace, job: AsyncJobRecord) -> None:
    atomic_write_text(
        _job_path(workspace, job.job_id),
        json.dumps(job.model_dump(mode="json"), indent=2, sort_keys=True),
        workspace.tmp_dir,
    )


def build_job_id(operation: str, request_hash: str) -> str:
    digest = stable_text_hash(f"job:{operation}:{request_hash}")
    return f"job_{digest[:20]}"


def create_or_reuse_job(
    workspace: SR8Workspace,
    *,
    operation: str,
    request_hash: str,
    actor_id: str,
    idempotency_key: str | None,
) -> tuple[AsyncJobRecord, bool]:
    workspace.initialize()
    with file_lock(workspace.jobs_lock_path):
        if idempotency_key:
            index = _load_idempotency_index(workspace)
            existing = index.get(idempotency_key)
            if existing is not None:
                if (
                    existing.get("request_hash") != request_hash
                    or existing.get("operation") != operation
                ):
                    msg = "Idempotency key reuse with a different request payload is not allowed."
                    raise ValueError(msg)
                return _read_job_unlocked(workspace, existing["job_id"]), True
        created_at = utc_now()
        job_seed = (
            f"{request_hash}:{idempotency_key}"
            if idempotency_key
            else f"{request_hash}:{actor_id}:{created_at.isoformat()}"
        )
        job = AsyncJobRecord(
            job_id=build_job_id(operation, job_seed),
            operation=operation,
            status="queued",
            request_hash=request_hash,
            workspace_root=str(workspace.root.resolve()),
            actor_id=actor_id,
            idempotency_key=idempotency_key,
            created_at=created_at,
        )
        _write_job_unlocked(workspace, job)
        if idempotency_key:
            index = _load_idempotency_index(workspace)
            index[idempotency_key] = {
                "job_id": job.job_id,
                "request_hash": request_hash,
                "operation": operation,
            }
            _save_idempotency_index(workspace, index)
        return job, False


def load_job(workspace: SR8Workspace, job_id: str) -> AsyncJobRecord:
    workspace.initialize()
    with file_lock(workspace.jobs_lock_path):
        return _read_job_unlocked(workspace, job_id)


def save_job(workspace: SR8Workspace, job: AsyncJobRecord) -> AsyncJobRecord:
    workspace.initialize()
    with file_lock(workspace.jobs_lock_path):
        _write_job_unlocked(workspace, job)
        return job
