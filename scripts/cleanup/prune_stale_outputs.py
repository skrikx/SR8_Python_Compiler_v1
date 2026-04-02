from __future__ import annotations

import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STALE_ROOTS = (
    REPO_ROOT / ".sr8" / "tmp",
    REPO_ROOT / ".mypy_cache",
    REPO_ROOT / ".pytest_cache",
    REPO_ROOT / ".ruff_cache",
    REPO_ROOT / "dist",
    REPO_ROOT / "build",
    REPO_ROOT / "frontend" / "node_modules",
    REPO_ROOT / "frontend" / ".npm-cache",
    REPO_ROOT / "frontend" / ".svelte-kit",
)
STALE_FILES = (
    REPO_ROOT / "examples" / "outputs" / "latest.json",
    REPO_ROOT / "examples" / "outputs" / "latest.md",
    REPO_ROOT / "SR8_updated_zip_audit.md",
    REPO_ROOT / "sr8_v1_compiler_first_run.txt",
)
STALE_GLOBS = (
    "examples/outputs/art_*.json",
    "*.zip",
)


def _remove_tree(path: Path, dry_run: bool) -> list[str]:
    removed: list[str] = []
    if not path.exists():
        return removed
    for child in sorted(path.rglob("*"), reverse=True):
        if child.is_file():
            removed.append(str(child.relative_to(REPO_ROOT)))
            if not dry_run:
                child.unlink()
    for child in sorted([item for item in path.rglob("*") if item.is_dir()], reverse=True):
        if not dry_run:
            try:
                child.rmdir()
            except OSError:
                continue
    if not dry_run:
        try:
            path.rmdir()
        except OSError:
            pass
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Prune known generated outputs.")
    parser.add_argument("--apply", action="store_true", help="Actually remove generated files.")
    args = parser.parse_args()
    dry_run = not args.apply
    for root in STALE_ROOTS:
        for removed in _remove_tree(root, dry_run=dry_run):
            print(f"{'would remove' if dry_run else 'removed'}: {removed}")
    for path in STALE_FILES:
        if path.exists():
            rel = str(path.relative_to(REPO_ROOT))
            print(f"{'would remove' if dry_run else 'removed'}: {rel}")
            if not dry_run:
                path.unlink()
    for pattern in STALE_GLOBS:
        for path in sorted(REPO_ROOT.glob(pattern)):
            if not path.is_file():
                continue
            rel = str(path.relative_to(REPO_ROOT))
            print(f"{'would remove' if dry_run else 'removed'}: {rel}")
            if not dry_run:
                path.unlink()
    if dry_run:
        print("dry run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
