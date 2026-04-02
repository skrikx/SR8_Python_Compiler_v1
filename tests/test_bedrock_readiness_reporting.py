from sr8.adapters.factory import create_provider


def test_bedrock_probe_reports_not_runtime_ready(monkeypatch) -> None:
    monkeypatch.setenv("SR8_AWS_BEDROCK_REGION", "us-east-1")
    monkeypatch.setenv("SR8_AWS_BEDROCK_MODEL", "anthropic.claude-v2")

    result = create_provider("aws_bedrock").probe()

    assert result.provider == "aws_bedrock"
    assert result.registered is True
    assert result.configured is True
    assert result.capable is True
    assert result.live_enabled is False
    assert result.ready_for_runtime is False
    assert result.available is False
    assert "SigV4" in result.detail
