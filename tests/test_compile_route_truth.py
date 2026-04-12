from sr8.compiler import compile_intent


def test_raw_one_line_semantic_compile_materially_expands_fields() -> None:
    result = compile_intent("Build a launch checklist for a local-first PRD compiler")
    artifact = result.artifact
    derived_fields = set(artifact.metadata["compiler_derived_fields"])

    assert artifact.metadata["compile_kind"] == "semantic_compile"
    assert artifact.metadata["semantic_transform_applied"] is True
    assert result.receipt.status == "accepted"
    assert {"scope", "constraints", "success_criteria", "output_contract"} <= derived_fields
    assert artifact.metadata["source_supplied_field_count"] == 0
    assert len(artifact.scope) >= 2
    assert len(artifact.constraints) >= 2
    assert len(artifact.success_criteria) >= 2
    assert len(artifact.output_contract) >= 2
    assert "semantic_expand" in [step.stage for step in artifact.lineage.steps]


def test_partial_markdown_semantic_compile_preserves_source_and_marks_derivations() -> None:
    result = compile_intent(
        (
            "# Objective\n"
            "Ship a governed API compile route\n\n"
            "## Scope\n"
            "- add truthful route metadata\n"
            "- keep structured JSON support\n"
        ),
        source_type="markdown",
    )
    artifact = result.artifact

    assert artifact.metadata["compile_kind"] == "semantic_compile"
    assert artifact.metadata["source_structure_kind"] == "markdown_outline"
    assert {"objective", "scope"} <= set(artifact.metadata["source_supplied_fields"])
    assert {
        "constraints",
        "success_criteria",
        "output_contract",
    } <= set(artifact.metadata["compiler_derived_fields"])
    assert artifact.metadata["weak_intent_recovery"]["intake_required"] is False


def test_structured_json_is_truthfully_classified_as_canonicalize_structured() -> None:
    result = compile_intent("tests/fixtures/input_json_payload.json", source_type="json")
    artifact = result.artifact

    assert artifact.metadata["compile_kind"] == "canonicalize_structured"
    assert artifact.metadata["semantic_transform_applied"] is False
    assert "objective" in artifact.metadata["source_supplied_fields"]
    assert "scope" in artifact.metadata["source_supplied_fields"]
    assert "scope" not in artifact.metadata["compiler_derived_fields"]
    assert result.receipt.status == "accepted"


def test_truly_weak_raw_text_is_rejected_as_needs_intake() -> None:
    result = compile_intent("help")
    artifact = result.artifact

    assert artifact.metadata["compile_kind"] == "needs_intake"
    assert artifact.validation.readiness_status == "fail"
    assert result.receipt.status == "rejected"
    assert artifact.metadata["weak_intent_recovery"]["intake_required"] is True
