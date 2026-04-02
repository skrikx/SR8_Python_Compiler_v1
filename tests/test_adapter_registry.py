from sr8.adapters import get_provider_descriptor, list_provider_descriptors, list_provider_names


def test_provider_registry_lists_wave_one_providers() -> None:
    assert list_provider_names() == (
        "openai",
        "azure_openai",
        "aws_bedrock",
        "anthropic",
        "gemini",
        "ollama",
    )


def test_provider_descriptors_include_capabilities() -> None:
    descriptors = list_provider_descriptors()
    assert len(descriptors) == 6
    assert all(descriptor.capabilities for descriptor in descriptors)
    assert get_provider_descriptor("openai").label == "OpenAI"
