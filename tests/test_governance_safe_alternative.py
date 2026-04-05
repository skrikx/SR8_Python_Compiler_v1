from sr8.compiler import compile_intent
from sr8.frontdoor.governance import evaluate_governance, suggest_safe_alternative
from sr8.frontdoor.xml_renderer import render_safe_alternative_package_xml
from sr8.models.intent_artifact import GovernanceFlags


def test_governance_safe_alternative_path() -> None:
    result = compile_intent("Objective: Build a plan\nScope:\n- step one")
    flagged = result.artifact.model_copy(
        update={"governance_flags": GovernanceFlags(requires_human_review=True)}
    )
    decision = evaluate_governance(flagged)
    assert decision.status == "safe_alternative_compile"
    xml = render_safe_alternative_package_xml(
        flagged,
        decision,
        suggest_safe_alternative(flagged),
    )
    assert "safe_alternative_package" in xml
