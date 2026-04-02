from __future__ import annotations

import os
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, cast

if os.name == "nt":
    import msvcrt
else:
    import fcntl as posix_fcntl


def atomic_write_text(path: Path, content: str, tmp_dir: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=tmp_dir,
        prefix=f"{path.stem}_",
        suffix=f"{path.suffix}.tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


@contextmanager
def file_lock(lock_path: Path) -> Iterator[None]:
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+b") as handle:
        if os.name == "nt":
            handle.seek(0)
            while True:
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
                    break
                except OSError:
                    time.sleep(0.01)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            cast_fcntl = cast(Any, posix_fcntl)
            cast_fcntl.flock(handle.fileno(), cast_fcntl.LOCK_EX)
            try:
                yield
            finally:
                cast_fcntl.flock(handle.fileno(), cast_fcntl.LOCK_UN)
