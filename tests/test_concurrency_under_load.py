import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app


def _submit_async_compile(index: int, workspace_root: Path) -> str:
    client = TestClient(app)
    response = client.post(
        "/compile",
        json={
            "source": f"Objective: Concurrent {index}\nScope:\n- item {index}\n",
            "rule_only": True,
            "async_mode": True,
            "idempotency_key": f"concurrent-{index}",
            "workspace_path": str(workspace_root),
        },
    )
    assert response.status_code == 202
    return response.json()["job"]["job_id"]


def test_async_jobs_complete_under_parallel_submission(tmp_path, monkeypatch) -> None:
    workspace_root = tmp_path / ".sr8"
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(workspace_root))
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(_submit_async_compile, index, workspace_root)
            for index in range(12)
        ]
        job_ids = [future.result() for future in futures]

    client = TestClient(app)
    pending = set(job_ids)
    for _ in range(80):
        completed: set[str] = set()
        for job_id in pending:
            response = client.get(f"/jobs/{job_id}")
            assert response.status_code == 200
            payload = response.json()["job"]
            if payload["status"] == "completed":
                completed.add(job_id)
        pending -= completed
        if not pending:
            break
        time.sleep(0.05)

    assert not pending
