from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PATHS = (
    ".github/workflows/ci.yml",
    ".github/workflows/reusable-test.yml",
    ".github/workflows/reusable-build.yml",
    ".github/workflows/docs-check.yml",
    ".github/workflows/frontend-ci.yml",
    ".github/workflows/hygiene.yml",
    ".github/workflows/release.yml",
    ".pre-commit-config.yaml",
    ".editorconfig",
    ".gitattributes",
    "RELEASE_CHECKLIST.md",
    "scripts/cleanup/repo_audit.py",
    "scripts/cleanup/prune_stale_outputs.py",
    "docs/install.md",
    "docs/repo-structure.md",
    "docs/examples.md",
    "docs/release-automation.md",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the normalized SR8 repository layout.")
    parser.parse_args()
    missing = [path for path in EXPECTED_PATHS if not (REPO_ROOT / path).exists()]
    if missing:
        for path in missing:
            print(f"missing: {path}")
        return 1
    print("repo layout ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
