from sr8.compiler import compile_intent
from sr8.frontdoor.governance import evaluate_governance, suggest_safe_alternative
from sr8.frontdoor.xml_renderer import (
    render_promptunit_package_xml,
    render_safe_alternative_package_xml,
    render_sr8_prompt_xml,
)


def test_xml_package_outputs_render() -> None:
    result = compile_intent("Objective: Build a launch plan\nScope:\n- Step one")
    governance = evaluate_governance(result.artifact)

    promptunit_xml = render_promptunit_package_xml(result.artifact, governance, result.receipt)
    sr8_prompt_xml = render_sr8_prompt_xml(result.artifact)
    safe_alt_xml = render_safe_alternative_package_xml(
        result.artifact,
        governance,
        suggest_safe_alternative(result.artifact),
    )

    assert promptunit_xml.startswith("<?xml")
    assert "<promptunit_package" in promptunit_xml
    assert "<sr8_prompt" in sr8_prompt_xml
    assert "<safe_alternative_package" in safe_alt_xml
