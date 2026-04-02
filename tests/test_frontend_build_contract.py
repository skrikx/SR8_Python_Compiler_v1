from pathlib import Path


def test_frontend_ci_contract_is_active() -> None:
    workflow = Path(".github/workflows/frontend-ci.yml").read_text(encoding="utf-8")

    assert "workflow_call" in workflow
    assert "actions/setup-node@v4" in workflow
    assert "frontend/package.json" in workflow
    assert "npm install" in workflow
    assert "npm run check" in workflow
    assert "npm run build" in workflow
    assert "deferred by design" not in workflow
