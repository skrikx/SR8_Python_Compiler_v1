from sr8.extract.adapters.registry import get_extraction_adapter


def test_extraction_trace_carries_recovery_contract() -> None:
    adapter = get_extraction_adapter("rule_based")
    _, trace = adapter.extract("Objective: Build tool\nScope:\n- parser\n")

    assert trace.recovery.intake_required is True
    assert "constraints" in trace.recovery.missing_fields
    assert "success_criteria" in trace.recovery.missing_fields
    assert trace.recovery.suggested_prompt


def test_contradictory_trace_marks_recovery_as_required() -> None:
    adapter = get_extraction_adapter("rule_based")
    _, trace = adapter.extract(
        "Objective: Audit repo\n"
        "Scope:\n- security checks\n"
        "Exclusions:\n- security checks\n"
    )

    assert trace.recovery.intake_required is True
    assert "scope" in trace.recovery.contradictory_fields
