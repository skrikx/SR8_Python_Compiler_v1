from __future__ import annotations

import pytest

from sr8.adapters.errors import ProviderNormalizationError
from sr8.adapters.types import ProviderResponse
from sr8.compiler import CompileConfig, compile_intent
from sr8.compiler.model_assist import run_model_assisted_extraction


class _DummyProvider:
    def __init__(self, content: str) -> None:
        self.content = content

    def complete(self, request):
        return ProviderResponse(
            provider=request.provider,
            model=request.model,
            content=self.content,
        )


VALID_RESPONSE = (
    '{"objective":"Assist compile","scope":["one"],"exclusions":[],"constraints":[],'
    '"context_package":[],"assumptions":[],"dependencies":[],"success_criteria":["done"],'
    '"output_contract":[],"target_class":"plan","authority_context":"team",'
    '"governance_flags":{"ambiguous":false,"incomplete":false,'
    '"requires_human_review":false}}'
)


def test_rules_mode_never_calls_provider(monkeypatch) -> None:
    def fail_provider(name: str):
        raise AssertionError(f"provider should not be called: {name}")

    monkeypatch.setattr("sr8.compiler.model_assist.create_provider", fail_provider)

    result = compile_intent(
        "Objective: Rules only\nScope:\n- one\n",
        config=CompileConfig(compile_mode="rules", assist_provider="openai", assist_model="gpt"),
    )

    assert result.receipt.assist_mode == "rules"
    assert result.receipt.llm_used is False
    assert result.receipt.provider is None


def test_assist_mode_records_provider_hashes(monkeypatch) -> None:
    monkeypatch.setattr(
        "sr8.compiler.model_assist.create_provider",
        lambda name: _DummyProvider(VALID_RESPONSE),
    )

    result = compile_intent(
        "Objective: Assist compile\nScope:\n- one\n",
        config=CompileConfig(
            compile_mode="assist",
            assist_provider="openai",
            assist_model="gpt-test",
        ),
    )

    assert result.artifact.objective == "Assist compile"
    assert result.receipt.llm_used is True
    assert result.receipt.provider == "openai"
    assert result.receipt.model == "gpt-test"
    assert result.receipt.prompt_hash
    assert result.receipt.raw_response_hash
    assert result.receipt.parsed_response_hash
    assert result.receipt.schema_validation_status == "pass"


def test_model_assist_invalid_json_rejects(monkeypatch) -> None:
    monkeypatch.setattr(
        "sr8.compiler.model_assist.create_provider",
        lambda name: _DummyProvider("not json"),
    )

    with pytest.raises(ProviderNormalizationError):
        run_model_assisted_extraction("Objective: Bad", "openai", "gpt-test")
