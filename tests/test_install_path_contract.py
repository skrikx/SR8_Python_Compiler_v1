from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_install_docs_match_python_version_contract() -> None:
    pyproject = _read("pyproject.toml")
    install_doc = _read("docs/install.md")
    readme = _read("README.md")

    assert 'requires-python = ">=3.11"' in pyproject
    assert "Python `>=3.11`" in install_doc
    assert "Python 3.11 or newer" in readme


def test_install_docs_cover_editable_dev_and_frontend_flows() -> None:
    install_doc = _read("docs/install.md")

    assert 'python -m pip install -e .' in install_doc
    assert 'python -m pip install -e ".[dev]"' in install_doc
    assert "npm ci" in install_doc
    assert ".env.example" in install_doc


def test_mkdocs_and_index_point_to_install_doc() -> None:
    mkdocs = _read("mkdocs.yml")
    index = _read("docs/index.md")

    assert "docs/install.md" in mkdocs
    assert "(install.md)" in index
