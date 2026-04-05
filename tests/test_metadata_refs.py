from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_readme_references_core_public_docs() -> None:
    readme = _read("README.md")
    assert "CONTRIBUTING.md" in readme
    assert "SECURITY.md" in readme
    assert "ROADMAP.md" in readme
    assert "docs/index.md" in readme
    assert "docs/public-api-exposure.md" in readme
    assert "actions/workflows/ci.yml/badge.svg" in readme
    assert "actions/workflows/docs-check.yml/badge.svg" in readme
    assert "actions/workflows/frontend-ci.yml/badge.svg" in readme
    assert "actions/workflows/hygiene.yml/badge.svg" in readme
    assert "actions/workflows/release.yml/badge.svg" in readme
    assert "actions/workflows/codeql.yml/badge.svg" in readme
    assert "assets/badges/README_BADGES.md" in readme


def test_docs_index_references_ops_pages() -> None:
    docs_index = _read("docs/index.md")
    assert "oss-launch.md" in docs_index
    assert "triage.md" in docs_index
    assert "release-notes-policy.md" in docs_index
    assert "post-launch-ops.md" in docs_index
    assert "bedrock-setup.md" in docs_index
    assert "public-api-exposure.md" in docs_index


def test_mkdocs_nav_includes_core_sections() -> None:
    mkdocs = _read("mkdocs.yml")
    assert "docs/index.md" in mkdocs
    assert "docs/cli-reference.md" in mkdocs
    assert "docs/python-api.md" in mkdocs
    assert "docs/bedrock-setup.md" in mkdocs
    assert "docs/public-api-exposure.md" in mkdocs
    assert "docs/examples.md" in mkdocs
    assert "docs/oss-launch.md" in mkdocs


def test_badge_asset_tracks_live_badge_surface() -> None:
    badge_plan = _read("assets/badges/README_BADGES.md")
    assert "actions/workflows/ci.yml/badge.svg" in badge_plan
    assert "actions/workflows/docs-check.yml/badge.svg" in badge_plan
    assert "actions/workflows/frontend-ci.yml/badge.svg" in badge_plan
    assert "actions/workflows/hygiene.yml/badge.svg" in badge_plan
    assert "actions/workflows/release.yml/badge.svg" in badge_plan
    assert "actions/workflows/codeql.yml/badge.svg" in badge_plan
    assert "do not expose a dependency-review badge" in badge_plan.lower()


def test_agents_carries_final_ship_law() -> None:
    agents = _read("AGENTS.md")
    assert "## Final Ship Law" in agents
    assert "## WF17 Validation Commands" in agents
    assert "docs/public-api-exposure.md" in agents
