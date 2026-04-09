from sr8.adapters import list_provider_descriptors, probe_providers
from sr8.compiler import CompileConfig, compile_intent


def test_provider_descriptors_expose_parity_metadata() -> None:
    descriptors = list_provider_descriptors()

    assert descriptors
    assert {descriptor.name for descriptor in descriptors} == {
        "openai",
        "azure_openai",
        "aws_bedrock",
        "anthropic",
        "gemini",
        "ollama",
    }
    assert all(descriptor.runtime_transport in {"http", "sdk"} for descriptor in descriptors)
    assert all(descriptor.assist_extract_supported is True for descriptor in descriptors)
    assert all(descriptor.default_model_env_var for descriptor in descriptors)


def test_provider_probes_expose_status_and_configured_model() -> None:
    probes = probe_providers()

    assert probes
    assert all(
        probe.status in {"ready", "bounded", "degraded", "missing_config"}
        for probe in probes
    )
    assert all(hasattr(probe, "configured_model") for probe in probes)


def test_model_assist_fallback_records_provider_failure(monkeypatch) -> None:
    def raise_error(name: str):
        from sr8.adapters.errors import ProviderExecutionError

        raise ProviderExecutionError(name, "provider unavailable")

    monkeypatch.setattr("sr8.compiler.model_assist.create_provider", raise_error)

    result = compile_intent(
        "Objective: Fallback metadata\nScope:\n- one\n",
        config=CompileConfig(
            extraction_adapter="model_assisted",
            assist_provider="openai",
            assist_model="gpt-test",
            assist_fallback_to_rule_based=True,
        ),
    )

    provider_assist = result.artifact.metadata["provider_assist"]

    assert provider_assist["assist_extract_status"] == "fallback_rule_based"
    assert provider_assist["assist_extract_route"] == "provider_failed_then_rule_based"
    assert provider_assist["fallback"] == "rule_based"
    assert provider_assist["error_type"] == "ProviderExecutionError"
