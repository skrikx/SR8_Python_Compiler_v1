from sr8.adapters.anthropic_adapter import AnthropicAdapter
from sr8.adapters.azure_openai_adapter import AzureOpenAIAdapter
from sr8.adapters.bedrock_adapter import BedrockAdapter
from sr8.adapters.gemini_adapter import GeminiAdapter
from sr8.adapters.ollama_adapter import OllamaAdapter
from sr8.adapters.openai_adapter import OpenAIAdapter
from sr8.config.provider_settings import (
    AnthropicProviderSettings,
    AWSBedrockProviderSettings,
    AzureOpenAIProviderSettings,
    GeminiProviderSettings,
    OllamaProviderSettings,
    OpenAIProviderSettings,
)


def test_openai_normalization_extracts_text() -> None:
    adapter = OpenAIAdapter(OpenAIProviderSettings(api_key="key", model="gpt-test"))
    result = adapter.normalize_response(
        {
            "model": "gpt-test",
            "choices": [
                {
                    "message": {"content": "hello"},
                    "finish_reason": "stop",
                }
            ],
        }
    )
    assert result.content == "hello"


def test_azure_openai_normalization_extracts_text() -> None:
    adapter = AzureOpenAIAdapter(
        AzureOpenAIProviderSettings(
            api_key="key",
            endpoint="https://example.openai.azure.com",
            deployment="chat",
            model="gpt-test",
        )
    )
    result = adapter.normalize_response(
        {
            "choices": [
                {
                    "message": {"content": [{"text": "azure"}]},
                    "finish_reason": "stop",
                }
            ]
        }
    )
    assert result.content == "azure"


def test_anthropic_normalization_extracts_text() -> None:
    adapter = AnthropicAdapter(AnthropicProviderSettings(api_key="key", model="claude"))
    result = adapter.normalize_response({"content": [{"text": "anthropic"}], "model": "claude"})
    assert result.content == "anthropic"


def test_gemini_normalization_extracts_text() -> None:
    adapter = GeminiAdapter(GeminiProviderSettings(api_key="key", model="gemini-pro"))
    result = adapter.normalize_response(
        {
            "candidates": [
                {
                    "content": {"parts": [{"text": "gemini"}]},
                    "finishReason": "STOP",
                }
            ]
        }
    )
    assert result.content == "gemini"


def test_ollama_normalization_extracts_text() -> None:
    adapter = OllamaAdapter(OllamaProviderSettings(model="llama3.1"))
    result = adapter.normalize_response({"response": "ollama", "model": "llama3.1"})
    assert result.content == "ollama"


def test_bedrock_normalization_extracts_text() -> None:
    adapter = BedrockAdapter(AWSBedrockProviderSettings(region="us-east-1", model="bedrock-model"))
    result = adapter.normalize_response(
        {
            "modelId": "bedrock-model",
            "output": {
                "message": {
                    "content": [{"text": "bedrock"}],
                }
            },
            "stopReason": "end_turn",
            "usage": {
                "inputTokens": 5,
                "outputTokens": 2,
                "totalTokens": 7,
            },
        }
    )
    assert result.content == "bedrock"
    assert result.finish_reason == "end_turn"
    assert result.usage == {
        "input_tokens": 5,
        "output_tokens": 2,
        "total_tokens": 7,
    }
