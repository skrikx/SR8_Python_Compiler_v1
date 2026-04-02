import httpx
import pytest

from sr8.adapters.errors import (
    ProviderExecutionError,
    ProviderNotConfiguredError,
    map_http_error,
)
from sr8.adapters.factory import create_provider


def test_unknown_provider_raises_value_error() -> None:
    with pytest.raises(ValueError):
        create_provider("unknown")


def test_map_http_error_uses_configuration_error_for_auth_failures() -> None:
    request = httpx.Request("POST", "https://example.com")
    response = httpx.Response(401, request=request)
    error = httpx.HTTPStatusError("boom", request=request, response=response)

    mapped = map_http_error("openai", error)

    assert isinstance(mapped, ProviderNotConfiguredError)


def test_map_http_error_uses_execution_error_for_other_statuses() -> None:
    request = httpx.Request("POST", "https://example.com")
    response = httpx.Response(500, request=request)
    error = httpx.HTTPStatusError("boom", request=request, response=response)

    mapped = map_http_error("openai", error)

    assert isinstance(mapped, ProviderExecutionError)
