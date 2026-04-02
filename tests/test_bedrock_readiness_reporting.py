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


class _SessionWithoutCredentials:
    def get_credentials(self) -> None:
        return None


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


class _ClientError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.response = {"Error": {"Code": code, "Message": message}}


def test_bedrock_probe_reports_missing_config() -> None:
    adapter = BedrockAdapter(AWSBedrockProviderSettings())

    result = adapter.probe()

    assert result.provider == "aws_bedrock"
    assert result.configured is False
    assert result.live_enabled is True
    assert result.ready_for_runtime is False
    assert "SR8_AWS_BEDROCK_REGION" in result.missing_env_vars
    assert "SR8_AWS_BEDROCK_MODEL" in result.missing_env_vars


def test_bedrock_probe_reports_missing_credentials(monkeypatch) -> None:
    adapter = BedrockAdapter(
        AWSBedrockProviderSettings(region="us-east-1", model="anthropic.claude-3-haiku")
    )
    monkeypatch.setattr(adapter, "_create_session", lambda: _SessionWithoutCredentials())

    result = adapter.probe()

    assert result.configured is False
    assert result.subscribed_or_accessible is None
    assert "credentials" in result.detail.lower()


def test_bedrock_probe_reports_access_denied(monkeypatch) -> None:
    adapter = BedrockAdapter(
        AWSBedrockProviderSettings(region="us-east-1", model="anthropic.claude-3-haiku")
    )
    monkeypatch.setattr(adapter, "_create_session", lambda: _SessionWithCredentials())

    def fake_client(session: object, service_name: str, timeout_seconds: float) -> object:
        del session, timeout_seconds
        if service_name == "bedrock":
            raise _ClientError("AccessDeniedException", "marketplace access missing")
        raise AssertionError("unexpected runtime client creation")

    monkeypatch.setattr(adapter, "_create_client", fake_client)

    result = adapter.probe()

    assert result.configured is True
    assert result.subscribed_or_accessible is False
    assert result.ready_for_runtime is False
    assert "access" in result.detail.lower()


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

    assert result.configured is True
    assert result.subscribed_or_accessible is True
    assert result.live_enabled is True
    assert result.ready_for_runtime is True
    assert result.available is True
