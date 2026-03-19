from __future__ import annotations

from pathlib import Path


def resolve_workspace_root(path: str | Path) -> Path:
    candidate = Path(path).resolve()
    if candidate.name == ".sr8":
        return candidate
    for current in (candidate, *candidate.parents):
        if current.name == ".sr8":
            return current
    return candidate / ".sr8"


def ensure_unique_path(base_path: Path) -> Path:
    if not base_path.exists():
        return base_path
    stem = base_path.stem
    suffix = base_path.suffix
    counter = 1
    while True:
        candidate = base_path.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1
