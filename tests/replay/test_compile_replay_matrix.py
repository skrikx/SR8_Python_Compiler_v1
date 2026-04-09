from fastapi.testclient import TestClient

from sr8.api.app import app


def test_sync_compile_replay_preserves_artifact_and_receipt_truth(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(app)
    payload = {
        "source": "Objective: Replay matrix\nScope:\n- one\nSuccess Criteria:\n- stable receipt\n",
        "profile": "generic",
        "rule_only": True,
        "idempotency_key": "sync-replay-1",
    }

    first = client.post("/compile", json=payload)
    second = client.post("/compile", json=payload)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["replayed"] is False
    assert second.json()["replayed"] is True
    assert first.json()["artifact"]["artifact_id"] == second.json()["artifact"]["artifact_id"]
    assert first.json()["receipt"]["receipt_id"] == second.json()["receipt"]["receipt_id"]
    assert (
        first.json()["artifact"]["lineage"]["compile_run_id"]
        == second.json()["artifact"]["lineage"]["compile_run_id"]
    )

