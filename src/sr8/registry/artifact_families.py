from __future__ import annotations

ARTIFACT_FAMILIES: tuple[str, ...] = (
    "canonical_artifact",
    "promptunit_package",
    "sr8_prompt",
    "landing_page_package",
    "mvp_builder_package",
    "deep_research_package",
    "task_graph",
    "governed_request_package",
    "multimodal_brief",
)


def list_artifact_families() -> tuple[str, ...]:
    return ARTIFACT_FAMILIES


def is_artifact_family(value: str) -> bool:
    return value in ARTIFACT_FAMILIES


def require_artifact_family(value: str) -> str:
    if value not in ARTIFACT_FAMILIES:
        msg = f"Unknown artifact family '{value}'."
        raise ValueError(msg)
    return value
