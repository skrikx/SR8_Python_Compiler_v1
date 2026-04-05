from sr8.adapters.bedrock_adapter import BedrockAdapter
from sr8.adapters.types import ProviderRequest
from sr8.config.provider_settings import AWSBedrockProviderSettings


class _FrozenCredentials:
    access_key = "AKIA_TEST"
    secret_key = "secret"


class _ResolvedCredentials:
    def get_frozen_credentials(self) -> _FrozenCredentials:
        return _FrozenCredentials()


class _SessionWithCredentials:
    def get_credentials(self) -> _ResolvedCredentials:
        return _ResolvedCredentials()


class _RuntimeClient:
    def converse(self, **_: object) -> dict[str, object]:
        return {
            "modelId": "anthropic.claude-3-haiku",
            "output": {"message": {"content": [{"text": "{\"objective\":\"Bedrock\"}"}]}},
            "stopReason": "end_turn",
            "usage": {
                "inputTokens": 11,
                "outputTokens": 4,
                "totalTokens": 15,
            },
        }


def test_bedrock_complete_uses_runtime_client(monkeypatch) -> None:
    adapter = BedrockAdapter(
        AWSBedrockProviderSettings(region="us-east-1", model="anthropic.claude-3-haiku")
    )
    monkeypatch.setattr(adapter, "_create_session", lambda: _SessionWithCredentials())
    monkeypatch.setattr(
        adapter,
        "_create_client",
        lambda session, service_name, timeout: _RuntimeClient(),
    )

    response = adapter.complete(
        ProviderRequest(
            provider="aws_bedrock",
            model="anthropic.claude-3-haiku",
            prompt="Return JSON",
            system_prompt="You are an SR8 extractor.",
            response_format="json",
        )
    )

    assert response.provider == "aws_bedrock"
    assert response.model == "anthropic.claude-3-haiku"
    assert response.content == "{\"objective\":\"Bedrock\"}"
    assert response.finish_reason == "end_turn"
    assert response.usage["total_tokens"] == 15
