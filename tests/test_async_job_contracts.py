import time

from fastapi.testclient import TestClient

from sr8.api.app import app


def test_async_compile_job_can_be_polled_to_completion(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(tmp_path / ".sr8"))
    client = TestClient(app)

    response = client.post(
        "/compile",
        json={
            "source": "Objective: Async compile\nScope:\n- one\n",
            "rule_only": True,
            "async_mode": True,
            "idempotency_key": "async-compile-1",
        },
    )

    assert response.status_code == 202
    job_id = response.json()["job"]["job_id"]

    for _ in range(50):
        job_response = client.get(f"/jobs/{job_id}")
        assert job_response.status_code == 200
        payload = job_response.json()
        if payload["job"]["status"] == "completed":
            assert payload["job"]["result_payload"]["artifact"]["objective"] == "Async compile"
            return
        time.sleep(0.05)

    raise AssertionError("async compile job did not complete in time")
