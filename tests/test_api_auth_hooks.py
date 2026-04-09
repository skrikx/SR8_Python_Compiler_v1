from fastapi.testclient import TestClient

from sr8.api.app import app


def test_safe_route_remains_open_when_auth_token_configured(monkeypatch) -> None:
    monkeypatch.setenv("SR8_API_AUTH_TOKEN", "secret-token")
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200


def test_compile_requires_bearer_token_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("SR8_API_AUTH_TOKEN", "secret-token")
    client = TestClient(app)

    denied = client.post(
        "/compile",
        json={"source": "Objective: Auth\nScope:\n- one\n", "rule_only": True},
    )
    allowed = client.post(
        "/compile",
        headers={"Authorization": "Bearer secret-token"},
        json={"source": "Objective: Auth\nScope:\n- one\n", "rule_only": True},
    )

    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "authentication_required"
    assert allowed.status_code == 200
    assert allowed.json()["request_identity"]["auth_mode"] == "bearer-token"


def test_rate_limit_hook_can_reject_repeated_requests(monkeypatch) -> None:
    monkeypatch.setenv("SR8_API_RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("SR8_API_RATE_LIMIT_WINDOW_SECONDS", "60")
    client = TestClient(app)

    first = client.post(
        "/compile",
        headers={"X-SR8-Actor": "rate-limit-test"},
        json={"source": "Objective: Limit\nScope:\n- one\n", "rule_only": True},
    )
    second = client.post(
        "/compile",
        headers={"X-SR8-Actor": "rate-limit-test"},
        json={"source": "Objective: Limit\nScope:\n- one\n", "rule_only": True},
    )

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "rate_limit_exceeded"
