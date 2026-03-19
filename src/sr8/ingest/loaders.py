from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import yaml

from sr8.models.source_intent import SourceIntent, SourceType
from sr8.utils.hash import stable_object_hash, stable_text_hash
from sr8.utils.ids import build_source_id

SUPPORTED_SOURCE_TYPES = {"text", "markdown", "json", "yaml"}


def _path_exists(candidate: str) -> bool:
    try:
        return Path(candidate).exists()
    except OSError:
        return False


def _detect_source_type(
    source: str | Path | Mapping[str, object],
    source_type: str | None,
) -> SourceType:
    if source_type is not None:
        normalized = source_type.lower().strip()
        if normalized not in SUPPORTED_SOURCE_TYPES:
            msg = f"Unsupported source_type '{source_type}'."
            raise ValueError(msg)
        return cast(SourceType, normalized)

    if isinstance(source, Mapping):
        return "json"

    if isinstance(source, Path):
        suffix = source.suffix.lower()
    elif isinstance(source, str) and _path_exists(source):
        suffix = Path(source).suffix.lower()
    else:
        return "text"

    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix == ".json":
        return "json"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    return "text"


def _as_text_lines(value: object, indent: int = 0) -> list[str]:
    prefix = "  " * indent
    if isinstance(value, Mapping):
        lines_map: list[str] = []
        for sub_key, sub_value in value.items():
            lines_map.append(f"{prefix}- {str(sub_key).replace('_', ' ')}:")
            lines_map.extend(_as_text_lines(sub_value, indent + 1))
        return lines_map
    if isinstance(value, list):
        lines_list: list[str] = []
        for item in value:
            if isinstance(item, (Mapping, list)):
                lines_list.append(f"{prefix}-")
                lines_list.extend(_as_text_lines(item, indent + 1))
            else:
                lines_list.append(f"{prefix}- {str(item).strip()}")
        return lines_list
    if value is None:
        return [f"{prefix}-"]
    return [f"{prefix}- {str(value).strip()}"]


def _mapping_to_intent_text(payload: Mapping[str, object]) -> str:
    blocks: list[str] = []
    for key, value in payload.items():
        heading = str(key).replace("_", " ").strip().title()
        blocks.append(f"{heading}:")
        blocks.extend(_as_text_lines(value))
        blocks.append("")
    return "\n".join(blocks).strip()


def _load_json(content: str) -> tuple[str, dict[str, object]]:
    parsed = json.loads(content)
    if isinstance(parsed, Mapping):
        payload = dict(parsed)
        return _mapping_to_intent_text(payload), payload
    return str(parsed), {"payload": parsed}


def _load_yaml(content: str) -> tuple[str, dict[str, object]]:
    parsed = yaml.safe_load(content)
    if isinstance(parsed, Mapping):
        payload = dict(parsed)
        return _mapping_to_intent_text(payload), payload
    return str(parsed), {"payload": parsed}


def load_source(
    source: str | Path | Mapping[str, object],
    source_type: str | None = None,
) -> SourceIntent:
    resolved_type = _detect_source_type(source, source_type)
    origin: str | None = None
    raw_content: str
    metadata: dict[str, object] = {"detected_source_type": resolved_type}

    if isinstance(source, Mapping):
        payload = dict(source)
        raw_content = _mapping_to_intent_text(payload)
        metadata["parsed_payload"] = payload
        source_hash = stable_object_hash(payload)
    else:
        text_input = str(source)
        if _path_exists(text_input):
            path_obj = Path(text_input)
            origin = str(path_obj.resolve())
            content = path_obj.read_text(encoding="utf-8")
        else:
            content = text_input

        if resolved_type in {"text", "markdown"}:
            raw_content = content
            source_hash = stable_text_hash(raw_content)
        elif resolved_type == "json":
            raw_content, payload = _load_json(content)
            metadata["parsed_payload"] = payload
            source_hash = stable_object_hash(payload)
        else:
            raw_content, payload = _load_yaml(content)
            metadata["parsed_payload"] = payload
            source_hash = stable_object_hash(payload)

    metadata["origin"] = origin or "inline"
    metadata["raw_char_count"] = len(raw_content)

    return SourceIntent(
        source_id=build_source_id(source_hash),
        source_type=resolved_type,
        raw_content=raw_content,
        normalized_content=raw_content,
        source_hash=source_hash,
        origin=origin,
        metadata=metadata,
    )
