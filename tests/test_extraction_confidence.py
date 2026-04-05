from sr8.extract.adapters.registry import get_extraction_adapter


def test_explicit_vs_inferred_signals() -> None:
    adapter = get_extraction_adapter("rule_based")
    _, trace = adapter.extract("Objective: Build tool\n")
    by_field = {signal.field_name: signal for signal in trace.confidence}
    assert by_field["objective"].status == "explicit"
    assert by_field["scope"].status == "empty"
    assert by_field["context_package"].status == "empty"


def test_contradictory_scope_signal_is_exposed() -> None:
    adapter = get_extraction_adapter("rule_based")
    _, trace = adapter.extract(
        "Objective: Build tool\n"
        "Scope:\n- parser\n"
        "Exclusions:\n- parser\n"
        "Context Package:\n- API doc\n"
    )
    by_field = {signal.field_name: signal for signal in trace.confidence}
    assert by_field["scope"].status == "contradictory"
    assert by_field["context_package"].status == "explicit"
