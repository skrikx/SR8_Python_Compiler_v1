from __future__ import annotations

from sr8.models.source_intent import SourceIntent
from sr8.utils.hash import stable_text_hash

WRAPPER_NOISE = {"```", "'''", '"""', "<<<", ">>>", "<intent>", "</intent>"}


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]

    while lines and lines[0].strip() in WRAPPER_NOISE:
        lines.pop(0)
    while lines and lines[-1].strip() in WRAPPER_NOISE:
        lines.pop()

    compact: list[str] = []
    blank_run = 0
    for line in lines:
        stripped = line.strip()
        if stripped in WRAPPER_NOISE:
            continue
        if stripped == "":
            blank_run += 1
            if blank_run <= 1:
                compact.append("")
            continue
        blank_run = 0
        compact.append(line)

    return "\n".join(compact).strip()


def normalize_source(source_intent: SourceIntent) -> SourceIntent:
    normalized = _normalize_text(source_intent.raw_content)
    normalized_hash = stable_text_hash(normalized)

    metadata = dict(source_intent.metadata)
    metadata["normalized_char_count"] = len(normalized)
    metadata["normalized_line_count"] = normalized.count("\n") + (1 if normalized else 0)
    metadata["normalization"] = "whitespace+wrapper-clean"
    metadata["normalized_source_hash"] = normalized_hash

    return source_intent.model_copy(
        update={
            "normalized_content": normalized,
            "metadata": metadata,
        }
    )
