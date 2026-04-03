from __future__ import annotations

from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _extract_pyproject_version(content: str) -> str:
    for line in content.splitlines():
        if line.startswith("version = "):
            return line.split("=", 1)[1].strip().strip('"')
    raise AssertionError("version not found in pyproject.toml")


def _extract_changelog_version(content: str) -> str:
    for line in content.splitlines():
        if line.startswith("## ["):
            return line.split("[", 1)[1].split("]", 1)[0]
    raise AssertionError("changelog version not found")


def test_release_metadata_versions_align() -> None:
    pyproject = _read("pyproject.toml")
    version_file = _read("src/sr8/version.py")
    changelog = _read("CHANGELOG.md")

    pyproject_version = _extract_pyproject_version(pyproject)
    changelog_version = _extract_changelog_version(changelog)
    version_constant = version_file.split("=", 1)[1].strip().strip('"')

    assert pyproject_version == version_constant
    assert changelog_version == pyproject_version


def test_release_badge_tag_matches_version() -> None:
    readme = _read("README.md")
    pyproject_version = _extract_pyproject_version(_read("pyproject.toml"))
    assert f"release.yml/badge.svg?tag=v{pyproject_version}" in readme
