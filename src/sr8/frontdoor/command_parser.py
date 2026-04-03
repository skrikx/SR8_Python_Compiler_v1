from __future__ import annotations

from typing import Literal

from pydantic import Field

from sr8.models.base import SR8Model
from sr8.registry.entry_modes import require_entry_mode

CommandAction = Literal["compile", "resume_intake"]


class ParsedCommand(SR8Model):
    action: CommandAction
    content: str
    raw: str
    entry_mode: str = Field(default="chat_compile")


def parse_chat_invocation(text: str) -> ParsedCommand:
    raw = text or ""
    stripped = raw.strip()
    lowered = stripped.lower()

    if lowered.startswith("resume:"):
        content = stripped[len("resume:") :].strip()
        entry_mode = require_entry_mode("intake_resume_compile")
        return ParsedCommand(
            action="resume_intake",
            content=content,
            raw=raw,
            entry_mode=entry_mode,
        )

    if lowered.startswith("compile:"):
        content = stripped[len("compile:") :].strip()
        entry_mode = require_entry_mode("chat_compile")
        return ParsedCommand(action="compile", content=content, raw=raw, entry_mode=entry_mode)

    if stripped.startswith("<COMPILER_INPUT_FORM") or "<COMPILER_INPUT_FORM" in stripped:
        entry_mode = require_entry_mode("intake_resume_compile")
        return ParsedCommand(
            action="resume_intake",
            content=stripped,
            raw=raw,
            entry_mode=entry_mode,
        )

    entry_mode = require_entry_mode("chat_compile")
    return ParsedCommand(action="compile", content=stripped, raw=raw, entry_mode=entry_mode)
