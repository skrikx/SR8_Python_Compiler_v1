import pytest

from sr8.adapters.bedrock_adapter import BedrockAdapter
from sr8.adapters.errors import ProviderExecutionError, ProviderNotConfiguredError
from sr8.adapters.types import ProviderRequest
from sr8.compiler import CompileConfig, compile_intent
from sr8.config.provider_settings import AWSBedrockProviderSettings


class _SessionWithoutCredentials:
    def get_credentials(self) -> None:
        return None


class _FrozenCredentials:
    access_key = "AKIA_TEST"
    secret_key = "secret"


class _ResolvedCredentials:
    def get_frozen_credentials(self) -> _FrozenCredentials:
        return _FrozenCredentials()


class _SessionWithCredentials:
    def get_credentials(self) -> _ResolvedCredentials:
        return _ResolvedCredentials()


class _ClientError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.response = {"Error": {"Code": code, "Message": message}}


class _DeniedRuntimeClient:
    def converse(self, **_: object) -> dict[str, object]:
        raise _ClientError("AccessDeniedException", "marketplace access missing")


def test_bedrock_complete_requires_credentials(monkeypatch) -> None:
    adapter = BedrockAdapter(
        AWSBedrockProviderSettings(region="us-east-1", model="anthropic.claude-3-haiku")
    )
    monkeypatch.setattr(adapter, "_create_session", lambda: _SessionWithoutCredentials())

    with pytest.raises(ProviderNotConfiguredError):
        adapter.complete(
            ProviderRequest(
                provider="aws_bedrock",
                model="anthropic.claude-3-haiku",
                prompt="Hello",
            )
        )


def test_bedrock_complete_reports_access_denied(monkeypatch) -> None:
    adapter = BedrockAdapter(
        AWSBedrockProviderSettings(region="us-east-1", model="anthropic.claude-3-haiku")
    )
    monkeypatch.setattr(adapter, "_create_session", lambda: _SessionWithCredentials())
    monkeypatch.setattr(
        adapter,
        "_create_client",
        lambda session, service_name, timeout: _DeniedRuntimeClient(),
    )

    with pytest.raises(ProviderExecutionError):
        adapter.complete(
            ProviderRequest(
                provider="aws_bedrock",
                model="anthropic.claude-3-haiku",
                prompt="Hello",
            )
        )


def test_rule_only_compile_is_unaffected_by_bedrock_settings(monkeypatch) -> None:
    monkeypatch.setenv("SR8_ASSIST_PROVIDER", "aws_bedrock")
    monkeypatch.setenv("SR8_ASSIST_MODEL", "anthropic.claude-3-haiku")

    result = compile_intent(
        "Objective: Rule only\nScope:\n- one\n",
        config=CompileConfig(profile="generic", extraction_adapter="rule_based"),
    )

    assert result.artifact.objective == "Rule only"
