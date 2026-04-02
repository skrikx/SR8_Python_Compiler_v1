from sr8.adapters.bedrock_adapter import BedrockAdapter
from sr8.adapters.types import ProviderRequest
from sr8.config.provider_settings import AWSBedrockProviderSettings


def test_bedrock_builds_converse_payload_with_system_prompt() -> None:
    adapter = BedrockAdapter(
        AWSBedrockProviderSettings(region="us-east-1", model="anthropic.claude-3-haiku")
    )

    payload = adapter._build_converse_payload(
        ProviderRequest(
            provider="aws_bedrock",
            model="anthropic.claude-3-haiku",
            prompt="Hello from SR8",
            system_prompt="Return JSON only.",
            temperature=0.2,
            max_tokens=120,
        )
    )

    assert payload["modelId"] == "anthropic.claude-3-haiku"
    assert payload["messages"] == [{"role": "user", "content": [{"text": "Hello from SR8"}]}]
    assert payload["system"] == [{"text": "Return JSON only."}]
    assert payload["inferenceConfig"] == {"temperature": 0.2, "maxTokens": 120}


def test_bedrock_builds_converse_payload_without_empty_system_prompt() -> None:
    adapter = BedrockAdapter(
        AWSBedrockProviderSettings(region="us-east-1", model="anthropic.claude-3-haiku")
    )

    payload = adapter._build_converse_payload(
        ProviderRequest(
            provider="aws_bedrock",
            model="anthropic.claude-3-haiku",
            prompt="Hello from SR8",
            system_prompt="",
        )
    )

    assert "system" not in payload
