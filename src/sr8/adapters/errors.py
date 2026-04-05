from __future__ import annotations

import httpx


class ProviderError(RuntimeError):
    def __init__(self, provider: str, message: str) -> None:
        super().__init__(message)
        self.provider = provider


class ProviderNotConfiguredError(ProviderError):
    pass


class ProviderExecutionError(ProviderError):
    pass


class ProviderNormalizationError(ProviderError):
    pass


def map_http_error(provider: str, error: httpx.HTTPError) -> ProviderError:
    if isinstance(error, httpx.HTTPStatusError):
        status_code = error.response.status_code
        if status_code in {401, 403}:
            return ProviderNotConfiguredError(
                provider,
                f"{provider} rejected the request. Check credentials and provider settings.",
            )
        return ProviderExecutionError(
            provider,
            f"{provider} request failed with HTTP {status_code}.",
        )
    return ProviderExecutionError(provider, f"{provider} request failed: {error}")
