from __future__ import annotations

DELIVERY_TARGETS: tuple[str, ...] = (
    "json_canonical",
    "xml_package",
    "markdown_derivative",
    "frontend_render",
    "future_orchestration_handoff",
)


def list_delivery_targets() -> tuple[str, ...]:
    return DELIVERY_TARGETS


def is_delivery_target(value: str) -> bool:
    return value in DELIVERY_TARGETS


def require_delivery_target(value: str) -> str:
    if value not in DELIVERY_TARGETS:
        msg = f"Unknown delivery target '{value}'."
        raise ValueError(msg)
    return value
