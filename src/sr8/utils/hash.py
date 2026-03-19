from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence


def stable_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_object_hash(payload: Mapping[str, object] | Sequence[object]) -> str:
    try:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except TypeError:
        canonical = repr(payload)
    return stable_text_hash(canonical)
