from __future__ import annotations


class SR8CompileError(ValueError):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class InvalidSourceInputError(SR8CompileError):
    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        super().__init__(
            code="invalid_source_input",
            message=message,
            details=details,
        )


class InvalidStructuredInputError(SR8CompileError):
    def __init__(
        self,
        source_type: str,
        message: str,
        details: dict[str, object] | None = None,
    ) -> None:
        super().__init__(
            code="invalid_structured_input",
            message=message,
            details={"source_type": source_type, **(details or {})},
        )
