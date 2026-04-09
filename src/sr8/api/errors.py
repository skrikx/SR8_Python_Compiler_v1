from __future__ import annotations


class SR8APIError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}

    def to_response(self) -> dict[str, object]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class InvalidRequestError(SR8APIError):
    def __init__(self, code: str, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__(status_code=422, code=code, message=message, details=details)


class PathInputDisallowedError(InvalidRequestError):
    def __init__(self, value: str) -> None:
        super().__init__(
            code="path_input_disallowed",
            message="API compile accepts inline source text or structured payloads only.",
            details={"input": value},
        )


class InvalidProviderError(InvalidRequestError):
    def __init__(self, provider: str) -> None:
        super().__init__(
            code="invalid_provider",
            message=f"Unknown provider '{provider}'.",
            details={"provider": provider},
        )


class InvalidConfigurationError(InvalidRequestError):
    def __init__(self, message: str) -> None:
        super().__init__(
            code="invalid_compile_configuration",
            message=message,
        )


class CompileBudgetExceededError(SR8APIError):
    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__(
            status_code=413,
            code="compile_budget_exceeded",
            message=message,
            details=details,
        )


class AuthenticationRequiredError(SR8APIError):
    def __init__(self) -> None:
        super().__init__(
            status_code=403,
            code="authentication_required",
            message="This route requires configured API authentication.",
            details={},
        )


class WorkspaceAccessDeniedError(SR8APIError):
    def __init__(self, requested_path: str) -> None:
        super().__init__(
            status_code=403,
            code="workspace_access_denied",
            message="Workspace override is denied by the current trusted-local policy.",
            details={"workspace_path": requested_path},
        )


class RateLimitExceededError(SR8APIError):
    def __init__(self, route_id: str, retry_after_seconds: int) -> None:
        super().__init__(
            status_code=429,
            code="rate_limit_exceeded",
            message="Rate limit exceeded for this route.",
            details={"route_id": route_id, "retry_after_seconds": retry_after_seconds},
        )


class ConcurrencyLimitExceededError(SR8APIError):
    def __init__(self) -> None:
        super().__init__(
            status_code=429,
            code="concurrency_limit_exceeded",
            message="Concurrent operation limit reached. Retry later.",
            details={},
        )


class IdempotencyConflictError(SR8APIError):
    def __init__(self) -> None:
        super().__init__(
            status_code=409,
            code="idempotency_conflict",
            message="Idempotency key cannot be reused with a different request payload.",
            details={},
        )


class AsyncJobsDisabledError(SR8APIError):
    def __init__(self) -> None:
        super().__init__(
            status_code=422,
            code="async_jobs_disabled",
            message="Async job mode is disabled in the current runtime configuration.",
            details={},
        )


class AsyncJobNotFoundError(SR8APIError):
    def __init__(self, job_id: str) -> None:
        super().__init__(
            status_code=404,
            code="job_not_found",
            message=f"Job '{job_id}' was not found.",
            details={"job_id": job_id},
        )


class ArtifactNotFoundError(SR8APIError):
    def __init__(self, path_or_id: str) -> None:
        super().__init__(
            status_code=404,
            code="artifact_not_found",
            message=f"Artifact '{path_or_id}' was not found.",
            details={"target": path_or_id},
        )


class InvalidArtifactPayloadError(InvalidRequestError):
    def __init__(self, path: str, reason: str) -> None:
        super().__init__(
            code="invalid_artifact_payload",
            message=f"Artifact '{path}' could not be parsed.",
            details={"path": path, "reason": reason},
        )


class UnsupportedArtifactContentError(SR8APIError):
    def __init__(self, path: str, reason: str) -> None:
        super().__init__(
            status_code=415,
            code="unsupported_artifact_content",
            message=f"Artifact '{path}' contains unsupported content.",
            details={"path": path, "reason": reason},
        )


class InvalidArtifactReferenceError(InvalidRequestError):
    def __init__(self, reference: str, reason: str) -> None:
        super().__init__(
            code="invalid_artifact_reference",
            message=reason,
            details={"reference": reference},
        )


class InvalidInspectTargetError(InvalidRequestError):
    def __init__(self, target: str) -> None:
        super().__init__(
            code="inspect_target_must_be_artifact",
            message=(
                "/inspect accepts a trusted-local artifact path "
                "or canonical artifact identifier."
            ),
            details={"target": target},
        )
