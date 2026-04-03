from __future__ import annotations

from sr8.compiler import CompileConfig, compile_intent
from sr8.frontdoor.command_parser import parse_chat_invocation
from sr8.frontdoor.governance import evaluate_governance, suggest_safe_alternative
from sr8.frontdoor.intake import extract_refined_intent, is_under_specified, render_intake_xml
from sr8.frontdoor.package_models import (
    FrontdoorCompileResult,
    FrontdoorStatus,
    GovernanceDecision,
)
from sr8.frontdoor.registry import require_artifact_family, require_delivery_target
from sr8.frontdoor.xml_renderer import (
    render_promptunit_package_xml,
    render_safe_alternative_package_xml,
    render_sr8_prompt_xml,
)
from sr8.models.intent_artifact import IntentArtifact


def chat_compile(source_text: str, config: CompileConfig | None = None) -> FrontdoorCompileResult:
    parsed = parse_chat_invocation(source_text)
    content = parsed.content.strip()
    entry_mode = parsed.entry_mode

    if parsed.action == "resume_intake":
        refined = extract_refined_intent(content)
        if not refined:
            intake_xml = render_intake_xml(content)
            return FrontdoorCompileResult(
                status="intake_required",
                entry_mode=entry_mode,
                artifact_family=require_artifact_family("governed_request_package"),
                delivery_target=require_delivery_target("xml_package"),
                governance=GovernanceDecision(status="deny", reason="intake_incomplete"),
                intake_xml=intake_xml,
                compile_config=config,
            )
        content = refined

    if is_under_specified(content):
        intake_xml = render_intake_xml(content)
        return FrontdoorCompileResult(
            status="intake_required",
            entry_mode=entry_mode,
            artifact_family=require_artifact_family("governed_request_package"),
            delivery_target=require_delivery_target("xml_package"),
            governance=GovernanceDecision(status="deny", reason="intake_required"),
            intake_xml=intake_xml,
            compile_config=config,
        )

    active_config = config or CompileConfig()
    compile_result = compile_intent(
        source=content,
        source_type="text",
        config=active_config,
    )

    governance = evaluate_governance(compile_result.artifact)
    promptunit_xml = render_promptunit_package_xml(
        compile_result.artifact,
        governance,
        compile_result.receipt,
    )
    sr8_prompt_xml = render_sr8_prompt_xml(compile_result.artifact)

    safe_alt_xml = None
    status: FrontdoorStatus = "compiled"
    if governance.status == "safe_alternative_compile":
        suggested = suggest_safe_alternative(compile_result.artifact)
        safe_alt_xml = render_safe_alternative_package_xml(
            compile_result.artifact,
            governance,
            suggested,
        )
        status = "safe_alternative"

    return FrontdoorCompileResult(
        status=status,
        entry_mode=entry_mode,
        artifact_family=require_artifact_family(_infer_artifact_family(compile_result.artifact)),
        delivery_target=require_delivery_target("xml_package"),
        governance=governance,
        artifact=compile_result.artifact,
        receipt=compile_result.receipt,
        normalized_source=compile_result.normalized_source,
        extracted_dimensions=compile_result.extracted_dimensions,
        promptunit_package_xml=promptunit_xml,
        sr8_prompt_xml=sr8_prompt_xml,
        safe_alternative_package_xml=safe_alt_xml,
        compile_config=active_config,
    )


def _infer_artifact_family(artifact: IntentArtifact) -> str:
    target = artifact.target_class.lower()
    mapping = {
        "landing_page": "landing_page_package",
        "mvp_builder": "mvp_builder_package",
        "deep_research": "deep_research_package",
        "governed_request": "governed_request_package",
        "multimodal_brief": "multimodal_brief",
        "code_task_graph": "task_graph",
    }
    if target in mapping:
        return mapping[target]
    return "promptunit_package"
