from sr8.extract.adapters.registry import get_extraction_adapter, list_extraction_adapters


def test_adapter_registry_has_rule_based() -> None:
    assert "rule_based" in list_extraction_adapters()
    adapter = get_extraction_adapter("rule_based")
    extracted, trace = adapter.extract("Objective: Ship tests\nScope:\n- One\n")
    assert extracted.objective == "Ship tests"
    assert trace.adapter_name == "rule_based"
    assert any(signal.field_name == "objective" for signal in trace.confidence)
