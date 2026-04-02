from __future__ import annotations

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
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        resolved = candidate.resolve(strict=False)
    else:
        resolved = (Path.cwd() / candidate).resolve(strict=False)

    allowed_roots = trusted_local_roots(extra_roots)
    if not any(resolved == root or resolved.is_relative_to(root) for root in allowed_roots):
        msg = f"Path '{resolved}' is outside the trusted local roots."
        raise ValueError(msg)
    if must_exist and not resolved.exists():
        raise FileNotFoundError(str(resolved))
    return resolved
