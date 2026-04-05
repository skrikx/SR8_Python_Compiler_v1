from __future__ import annotations

import os
import tempfile
from collections.abc import Iterable
from pathlib import Path


def trusted_local_roots(extra_roots: Iterable[str | Path] | None = None) -> tuple[Path, ...]:
    roots: list[Path] = [
        Path.cwd(),
        Path.home(),
        Path(tempfile.gettempdir()),
    ]
    if extra_roots is not None:
        roots.extend(Path(root) for root in extra_roots)

    normalized: list[Path] = []
    for root in roots:
        resolved = root.expanduser().resolve(strict=False)
        if resolved not in normalized:
            normalized.append(resolved)
    return tuple(normalized)


def resolve_trusted_local_path(
    value: str | Path,
    *,
    extra_roots: Iterable[str | Path] | None = None,
    must_exist: bool = False,
) -> Path:
    candidate_text = os.path.normpath(os.path.expanduser(str(value).strip()))
    if not candidate_text or "\x00" in candidate_text:
        msg = "Path value must be a non-empty local path."
        raise ValueError(msg)
    absolute_candidate = os.path.abspath(candidate_text)
    allowed_roots = trusted_local_roots(extra_roots)
    for root in allowed_roots:
        root_text = os.path.abspath(str(root))
        relative_tail = os.path.relpath(absolute_candidate, root_text)
        if relative_tail == ".":
            resolved = root
        elif relative_tail.startswith("..") or os.path.isabs(relative_tail):
            continue
        else:
            parts = [part for part in relative_tail.split(os.sep) if part not in {"", "."}]
            resolved = root.joinpath(*parts).resolve(strict=False)
        if must_exist and not resolved.exists():
            raise FileNotFoundError(str(resolved))
        return resolved
    msg = f"Path '{absolute_candidate}' is outside the trusted local roots."
    raise ValueError(msg)
