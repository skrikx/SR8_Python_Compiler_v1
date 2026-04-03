from __future__ import annotations

ENTRY_MODES: tuple[str, ...] = (
    "file_compile",
    "api_compile",
    "frontend_compile",
    "chat_compile",
    "intake_resume_compile",
)


def list_entry_modes() -> tuple[str, ...]:
    return ENTRY_MODES


def is_entry_mode(value: str) -> bool:
    return value in ENTRY_MODES


def require_entry_mode(value: str) -> str:
    if value not in ENTRY_MODES:
        msg = f"Unknown entry mode '{value}'."
        raise ValueError(msg)
    return value
