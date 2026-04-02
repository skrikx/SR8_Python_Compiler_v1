from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_release_and_ci_workflow_contracts() -> None:
    release = _read(".github/workflows/release.yml")
    ci = _read(".github/workflows/ci.yml")
    docs_check = _read(".github/workflows/docs-check.yml")
    frontend_ci = _read(".github/workflows/frontend-ci.yml")
    hygiene = _read(".github/workflows/hygiene.yml")

    assert "v*.*.*" in release
    assert "pypa/gh-action-pypi-publish@release/v1" in release
    assert "softprops/action-gh-release@v2" in release
    assert "workflow_dispatch" in release

    assert "docs-check" in ci
    assert "frontend-ci" in ci
    assert "hygiene" in ci
    assert "package-build-smoke" in ci
    assert "docs-check, hygiene, frontend-ci" in ci

    assert "workflow_call" in docs_check
    assert "tests/test_repo_structure.py" in docs_check
    assert "tests/test_release_workflow_contracts.py" in docs_check

    assert "workflow_call" in frontend_ci
    assert "frontend/package.json" in frontend_ci
    assert "actions/setup-node@v4" in frontend_ci
    assert "npm run build" in frontend_ci

    assert "workflow_call" in hygiene
    assert "repo layout check" in hygiene
    assert "repo audit" in hygiene
