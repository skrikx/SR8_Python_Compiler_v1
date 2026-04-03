from __future__ import annotations

from sr8.transform.renderers.markdown_plan import render_markdown_plan
from sr8.transform.renderers.markdown_prd import render_markdown_prd
from sr8.transform.renderers.markdown_procedure import render_markdown_procedure
from sr8.transform.renderers.markdown_prompt_pack import render_markdown_prompt_pack
from sr8.transform.renderers.markdown_research_brief import render_markdown_research_brief
from sr8.transform.renderers.xml_promptunit_package import render_xml_promptunit_package
from sr8.transform.renderers.xml_safe_alternative_package import (
    render_xml_safe_alternative_package,
)
from sr8.transform.renderers.xml_sr8_prompt import render_xml_sr8_prompt
from sr8.transform.types import TransformTargetSpec

TRANSFORM_REGISTRY: dict[str, TransformTargetSpec] = {
    "markdown_prd": TransformTargetSpec(
        target="markdown_prd",
        description="Render PRD-style markdown output.",
        renderer=render_markdown_prd,
        compatible_profiles=("prd",),
    ),
    "markdown_plan": TransformTargetSpec(
        target="markdown_plan",
        description="Render planning markdown output.",
        renderer=render_markdown_plan,
        compatible_profiles=(
            "generic",
            "plan",
            "prd",
            "repo_audit",
            "procedure",
            "research_brief",
            "whitepaper_outline",
            "code_task_graph",
        ),
    ),
    "markdown_research_brief": TransformTargetSpec(
        target="markdown_research_brief",
        description="Render research brief markdown output.",
        renderer=render_markdown_research_brief,
        compatible_profiles=("research_brief", "repo_audit"),
    ),
    "markdown_procedure": TransformTargetSpec(
        target="markdown_procedure",
        description="Render procedure markdown output.",
        renderer=render_markdown_procedure,
        compatible_profiles=("procedure",),
    ),
    "markdown_prompt_pack": TransformTargetSpec(
        target="markdown_prompt_pack",
        description="Render reusable prompt pack markdown output.",
        renderer=render_markdown_prompt_pack,
        compatible_profiles=(
            "prompt_pack",
            "plan",
            "prd",
            "generic",
            "media_spec",
            "whitepaper_outline",
            "code_task_graph",
        ),
    ),
    "xml_promptunit_package": TransformTargetSpec(
        target="xml_promptunit_package",
        description="Render promptunit package XML output.",
        renderer=render_xml_promptunit_package,
        compatible_profiles=(
            "generic",
            "plan",
            "prd",
            "procedure",
            "prompt_pack",
            "research_brief",
            "repo_audit",
            "whitepaper_outline",
            "code_task_graph",
            "media_spec",
        ),
    ),
    "xml_sr8_prompt": TransformTargetSpec(
        target="xml_sr8_prompt",
        description="Render SR8 prompt XML output.",
        renderer=render_xml_sr8_prompt,
        compatible_profiles=(
            "generic",
            "plan",
            "prd",
            "procedure",
            "prompt_pack",
            "research_brief",
            "repo_audit",
            "whitepaper_outline",
            "code_task_graph",
            "media_spec",
        ),
    ),
    "xml_safe_alternative_package": TransformTargetSpec(
        target="xml_safe_alternative_package",
        description="Render governance-safe alternative XML package.",
        renderer=render_xml_safe_alternative_package,
        compatible_profiles=(
            "generic",
            "plan",
            "prd",
            "procedure",
            "prompt_pack",
            "research_brief",
            "repo_audit",
            "whitepaper_outline",
            "code_task_graph",
            "media_spec",
        ),
    ),
}


def get_transform_target(target: str) -> TransformTargetSpec:
    key = target.strip().lower()
    if key not in TRANSFORM_REGISTRY:
        msg = f"Unknown transform target '{target}'."
        raise ValueError(msg)
    return TRANSFORM_REGISTRY[key]


def list_transform_targets() -> tuple[str, ...]:
    return tuple(TRANSFORM_REGISTRY.keys())
