from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx
else:  # pragma: no cover - import guard for local rule-only paths
    try:
        import httpx
    except ModuleNotFoundError:  # pragma: no cover - optional runtime dependency
        httpx = None  # type: ignore[assignment]


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


def map_http_error(provider: str, error: Any) -> ProviderError:
    if httpx is not None and isinstance(error, httpx.HTTPStatusError):
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
