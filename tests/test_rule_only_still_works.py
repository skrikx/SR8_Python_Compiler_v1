from sr8.compiler import CompileConfig, compile_intent


def test_rule_only_compile_still_works_without_provider_configuration() -> None:
    result = compile_intent(
        "Objective: Ship local compile\nScope:\n- one\n",
        config=CompileConfig(profile="generic", extraction_adapter="rule_based"),
    )

    assert result.artifact.objective == "Ship local compile"
    assert result.artifact.metadata["extraction_trust_summary"]["provider"] is None
