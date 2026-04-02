from pathlib import Path

from fastapi.testclient import TestClient

from sr8.api.app import app


def test_api_compile_rejects_local_file_paths(tmp_path: Path) -> None:
    secret_path = tmp_path / "secret.txt"
    secret_path.write_text("TOP SECRET CONTENT", encoding="utf-8")
    client = TestClient(app)

    response = client.post("/compile", json={"source": str(secret_path), "profile": "generic"})

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "path_input_disallowed"
    assert "TOP SECRET CONTENT" not in response.text


def test_api_compile_accepts_structured_payload() -> None:
    client = TestClient(app)

    response = client.post(
        "/compile",
        json={
            "source_payload": {
                "objective": "Structured compile contract",
                "scope": ["one"],
            },
            "profile": "generic",
            "rule_only": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["artifact"]["objective"] == "Structured compile contract"
