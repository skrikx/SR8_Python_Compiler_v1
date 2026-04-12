from sr8.compiler import compile_intent
from sr8.frontdoor.chat_compile import chat_compile
from sr8.frontdoor.intake import analyze_intent_surface


def test_compile_marks_semantic_recovery_when_partial_markdown_is_completed() -> None:
    artifact = compile_intent("Objective: Build tool\nScope:\n- parser\n").artifact
    recovery = artifact.metadata["weak_intent_recovery"]

    assert artifact.metadata["compile_kind"] == "semantic_compile"
    assert artifact.metadata["semantic_transform_applied"] is True
    assert recovery["intake_required"] is False
    assert recovery["recovery_applied"] is True
    assert "constraints" in recovery["recovered_fields"]
    assert "constraints" in artifact.metadata["compiler_derived_fields"]
    assert "success_criteria" in artifact.metadata["compiler_derived_fields"]
    assert "output_contract" in artifact.metadata["compiler_derived_fields"]


def test_compile_requires_intake_for_truly_weak_raw_intent() -> None:
    artifact = compile_intent("Need something helpful soon.").artifact

    assert artifact.metadata["compile_kind"] == "needs_intake"
    assert artifact.metadata["weak_intent_recovery"]["intake_required"] is True
    assert any(issue.code == "VAL-ROUTE-004" for issue in artifact.validation.errors)


def test_frontdoor_uses_recovery_analysis_for_under_specified_intent() -> None:
    analysis = analyze_intent_surface("build something fast")
    result = chat_compile("compile: build something fast")

    assert analysis["intake_required"] is True
    assert analysis["recovery"]["suggested_prompt"]
    assert result.status == "intake_required"
    assert result.intake_xml is not None
