from sr8.compiler import compile_intent
from sr8.frontdoor.chat_compile import chat_compile
from sr8.frontdoor.intake import analyze_intent_surface


def test_compile_attaches_structured_weak_intent_recovery() -> None:
    artifact = compile_intent("Objective: Build tool\nScope:\n- parser\n").artifact
    recovery = artifact.metadata["weak_intent_recovery"]

    assert recovery["intake_required"] is True
    assert "constraints" in recovery["missing_fields"]
    assert any(issue.code == "VAL-REC-001" for issue in artifact.validation.warnings)


def test_frontdoor_uses_recovery_analysis_for_under_specified_intent() -> None:
    analysis = analyze_intent_surface("build something fast")
    result = chat_compile("compile: build something fast")

    assert analysis["intake_required"] is True
    assert analysis["recovery"]["suggested_prompt"]
    assert result.status == "intake_required"
    assert result.intake_xml is not None
