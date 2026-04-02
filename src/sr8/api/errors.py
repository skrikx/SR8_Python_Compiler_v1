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
