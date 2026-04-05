from __future__ import annotations

from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_readme_badges_match_badge_plan() -> None:
    readme = _read("README.md")
    badge_plan = _read("assets/badges/README_BADGES.md")

    for needle in (
        "actions/workflows/ci.yml/badge.svg?branch=main",
        "actions/workflows/docs-check.yml/badge.svg?branch=main",
        "actions/workflows/frontend-ci.yml/badge.svg?branch=main",
        "actions/workflows/hygiene.yml/badge.svg?branch=main",
        "actions/workflows/release.yml/badge.svg?tag=v1.2.4",
        "actions/workflows/codeql.yml/badge.svg?branch=main",
        "img.shields.io/github/v/release/skrikx/SR8_Python_Compiler_v1",
    ):
        assert needle in readme
        assert needle in badge_plan


def test_readme_badges_link_to_workflows() -> None:
    readme = _read("README.md")
    for workflow in (
        "ci.yml",
        "docs-check.yml",
        "frontend-ci.yml",
        "hygiene.yml",
        "release.yml",
        "codeql.yml",
    ):
        assert f"actions/workflows/{workflow}" in readme
