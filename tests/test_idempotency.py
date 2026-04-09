from fastapi.testclient import TestClient

from sr8.api.app import app


def test_async_compile_reuses_job_for_same_idempotency_key(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(app)
    payload = {
        "source": "Objective: Replay-safe\nScope:\n- one\n",
        "rule_only": True,
        "async_mode": True,
        "idempotency_key": "idem-1",
    }

    first = client.post("/compile", json=payload)
    second = client.post("/compile", json=payload)

    assert first.status_code == 202
    assert second.status_code == 202
    assert first.json()["job"]["job_id"] == second.json()["job"]["job_id"]
    assert second.json()["replayed"] is True


def test_idempotency_key_conflict_maps_to_409(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(app)

    first = client.post(
        "/compile",
        json={
            "source": "Objective: Replay-safe\nScope:\n- one\n",
            "rule_only": True,
            "async_mode": True,
            "idempotency_key": "idem-conflict",
        },
    )
    second = client.post(
        "/compile",
        json={
            "source": "Objective: Different\nScope:\n- two\n",
            "rule_only": True,
            "async_mode": True,
            "idempotency_key": "idem-conflict",
        },
    )

    assert first.status_code == 202
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "idempotency_conflict"
