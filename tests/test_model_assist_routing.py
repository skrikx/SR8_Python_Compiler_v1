from sr8.compiler import CompileConfig, compile_intent


class _DummyProvider:
    def complete(self, request):
        from sr8.adapters.types import ProviderResponse

        return ProviderResponse(
            provider=request.provider,
            model=request.model,
            content=(
                '{"objective":"Assist compile","scope":["one"],"exclusions":[],'
                '"constraints":[],"context_package":[],"assumptions":[],"dependencies":[],'
                '"success_criteria":["done"],"output_contract":[],"target_class":"plan",'
                '"authority_context":"team","governance_flags":{"ambiguous":false,'
                '"incomplete":false,"requires_human_review":false}}'
            ),
        )


def test_model_assisted_compile_routes_provider_metadata(monkeypatch) -> None:
    monkeypatch.setattr("sr8.compiler.model_assist.create_provider", lambda name: _DummyProvider())

    result = compile_intent(
        "Objective: Assist compile\nScope:\n- one\n",
        config=CompileConfig(
            profile="generic",
            extraction_adapter="model_assisted",
            assist_provider="openai",
            assist_model="gpt-test",
        ),
    )

    assert result.artifact.objective == "Assist compile"
    assert result.artifact.metadata["provider_assist"]["provider"] == "openai"
    assert result.artifact.metadata["extraction_trust_summary"]["provider"] == "openai"


def test_model_assisted_falls_back_to_rule_based(monkeypatch) -> None:
    def raise_error(name: str):
        from sr8.adapters.errors import ProviderExecutionError

        raise ProviderExecutionError(name, "down")

    monkeypatch.setattr("sr8.compiler.model_assist.create_provider", raise_error)

    result = compile_intent(
        "Objective: Fallback path\nScope:\n- one\n",
        config=CompileConfig(
            extraction_adapter="model_assisted",
            assist_provider="openai",
            assist_model="gpt-test",
            assist_fallback_to_rule_based=True,
        ),
    )

    assert result.artifact.objective == "Fallback path"
    assert result.artifact.metadata["provider_assist"]["fallback"] == "rule_based"
