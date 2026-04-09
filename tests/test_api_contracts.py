from fastapi.testclient import TestClient

from sr8.api.app import app


def test_openapi_exposes_route_contract_metadata() -> None:
    client = TestClient(app)

    payload = client.get("/openapi.json").json()
    compile_operation = payload["paths"]["/compile"]["post"]
    inspect_operation = payload["paths"]["/inspect"]["post"]

    assert compile_operation["x-sr8-route-contract"]["exposure_class"] == "deliberate-exposure"
    assert inspect_operation["x-sr8-route-contract"]["exposure_class"] == "trusted-local"


def test_compile_response_carries_route_contract() -> None:
    client = TestClient(app)

    response = client.post(
        "/compile",
        json={"source": "Objective: API contract\nScope:\n- one\n", "rule_only": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["route_contract"]["route_id"] == "compile"
    assert payload["route_contract"]["path_policy"] == "inline-source-or-structured-payload-only"
