from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import yaml

from sr8.compiler.errors import InvalidSourceInputError, InvalidStructuredInputError
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
        if isinstance(source, str):
            stripped = source.strip()
            if stripped.startswith(("{", "[")):
                try:
                    parsed = json.loads(stripped)
                except json.JSONDecodeError:
                    pass
                else:
                    if isinstance(parsed, (Mapping, list)):
                        return "json"
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
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise InvalidStructuredInputError(
            "json",
            "JSON source could not be parsed.",
            details={"reason": "invalid_json", "line": exc.lineno, "column": exc.colno},
        ) from exc
    if isinstance(parsed, Mapping):
        payload = dict(parsed)
        if not payload:
            raise InvalidStructuredInputError(
                "json",
                "JSON source must contain at least one field.",
                details={"reason": "empty_object"},
            )
        return _mapping_to_intent_text(payload), payload
    if isinstance(parsed, list):
        if not parsed:
            raise InvalidStructuredInputError(
                "json",
                "JSON source list must contain at least one item.",
                details={"reason": "empty_list"},
            )
        return _mapping_to_intent_text({"payload": parsed}), {"payload": parsed}
    return str(parsed), {"payload": parsed}


def _load_yaml(content: str) -> tuple[str, dict[str, object]]:
    try:
        parsed = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise InvalidStructuredInputError(
            "yaml",
            "YAML source could not be parsed.",
            details={"reason": "invalid_yaml"},
        ) from exc
    if isinstance(parsed, Mapping):
        payload = dict(parsed)
        if not payload:
            raise InvalidStructuredInputError(
                "yaml",
                "YAML source must contain at least one field.",
                details={"reason": "empty_object"},
            )
        return _mapping_to_intent_text(payload), payload
    if isinstance(parsed, list):
        if not parsed:
            raise InvalidStructuredInputError(
                "yaml",
                "YAML source list must contain at least one item.",
                details={"reason": "empty_list"},
            )
        return _mapping_to_intent_text({"payload": parsed}), {"payload": parsed}
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
        if not payload:
            raise InvalidSourceInputError(
                "Structured source payload is empty.",
                details={"source_type": resolved_type},
            )
        raw_content = _mapping_to_intent_text(payload)
        metadata["parsed_payload"] = payload
        source_hash = stable_object_hash(payload)
        metadata["ingest_mode"] = "mapping"
    else:
        text_input = str(source)
        if _path_exists(text_input):
            path_obj = Path(text_input)
            origin = str(path_obj.resolve())
            content = path_obj.read_text(encoding="utf-8")
            metadata["ingest_mode"] = "path"
        else:
            content = text_input
            metadata["ingest_mode"] = "inline"

        if not content.strip():
            raise InvalidSourceInputError(
                "Source text is empty after trimming whitespace.",
                details={"source_type": resolved_type},
            )

        if resolved_type in {"text", "markdown"}:
            raw_content = content
            source_hash = stable_text_hash(raw_content)
        elif resolved_type == "json":
            raw_content, payload = _load_json(content)
            metadata["parsed_payload"] = payload
            source_hash = stable_object_hash(payload)
            metadata["structured_payload_kind"] = "json"
        else:
            raw_content, payload = _load_yaml(content)
            metadata["parsed_payload"] = payload
            source_hash = stable_object_hash(payload)
            metadata["structured_payload_kind"] = "yaml"

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
