from sr8.adapters.bedrock_adapter import BedrockAdapter
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


class _SuccessControlClient:
    def get_foundation_model(self, *, modelIdentifier: str) -> dict[str, object]:
        return {"modelId": modelIdentifier}


class _SuccessRuntimeClient:
    def converse(self, **_: object) -> dict[str, object]:
        return {
            "modelId": "anthropic.claude-3-haiku-20240307-v1:0",
            "output": {"message": {"content": [{"text": "ready"}]}},
            "stopReason": "end_turn",
        }


def test_bedrock_descriptor_reports_sdk_transport() -> None:
    descriptor = BedrockAdapter(AWSBedrockProviderSettings()).describe()

    assert descriptor.runtime_transport == "sdk"
    assert descriptor.default_model_env_var == "SR8_AWS_BEDROCK_MODEL"


def test_bedrock_probe_without_runtime_smoke_stays_bounded(monkeypatch) -> None:
    adapter = BedrockAdapter(
        AWSBedrockProviderSettings(region="us-east-1", model="anthropic.claude-3-haiku")
    )
    monkeypatch.setattr(adapter, "_create_session", lambda: _SessionWithCredentials())
    monkeypatch.setattr(
        adapter,
        "_create_client",
        lambda session, service_name, timeout_seconds: _SuccessControlClient(),
    )

    result = adapter.probe()

    assert result.status == "bounded"
    assert result.configured is True
    assert result.requires_live_probe is True
    assert result.ready_for_runtime is False


def test_bedrock_probe_runtime_smoke_marks_ready(monkeypatch) -> None:
    adapter = BedrockAdapter(
        AWSBedrockProviderSettings(
            region="us-east-1",
            model="anthropic.claude-3-haiku",
            probe_runtime=True,
        )
    )
    monkeypatch.setattr(adapter, "_create_session", lambda: _SessionWithCredentials())

    def fake_client(session: object, service_name: str, timeout_seconds: float) -> object:
        del session, timeout_seconds
        if service_name == "bedrock":
            return _SuccessControlClient()
        if service_name == "bedrock-runtime":
            return _SuccessRuntimeClient()
        raise AssertionError(f"unexpected service {service_name}")

    monkeypatch.setattr(adapter, "_create_client", fake_client)

    result = adapter.probe()

    assert result.status == "ready"
    assert result.ready_for_runtime is True
    assert result.requires_live_probe is False
