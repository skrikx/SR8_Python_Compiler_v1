from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_readme_references_core_public_docs() -> None:
    readme = _read("README.md")
    assert "CONTRIBUTING.md" in readme
    assert "SECURITY.md" in readme
    assert "ROADMAP.md" in readme
    assert "docs/index.md" in readme


def test_docs_index_references_ops_pages() -> None:
    docs_index = _read("docs/index.md")
    assert "oss-launch.md" in docs_index
    assert "triage.md" in docs_index
    assert "release-notes-policy.md" in docs_index
    assert "post-launch-ops.md" in docs_index


def test_mkdocs_nav_includes_core_sections() -> None:
    mkdocs = _read("mkdocs.yml")
    assert "docs/index.md" in mkdocs
    assert "docs/cli-reference.md" in mkdocs
    assert "docs/python-api.md" in mkdocs
    assert "docs/examples.md" in mkdocs
    assert "docs/oss-launch.md" in mkdocs
