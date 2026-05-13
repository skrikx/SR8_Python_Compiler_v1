from __future__ import annotations

import json
import re
import threading
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path

import yaml
from fastapi import Request
from pydantic import ValidationError

from sr8.adapters import list_provider_names
from sr8.api.errors import (
    ArtifactNotFoundError,
    AuthenticationRequiredError,
    CompileBudgetExceededError,
    ConcurrencyLimitExceededError,
    InvalidArtifactPayloadError,
    InvalidArtifactReferenceError,
    InvalidConfigurationError,
    InvalidInspectTargetError,
    InvalidProviderError,
    PathInputDisallowedError,
    RateLimitExceededError,
    UnsupportedArtifactContentError,
    WorkspaceAccessDeniedError,
)
from sr8.api.schemas import CompileRequest, RequestIdentity, RouteExposureClass
from sr8.compiler.errors import SR8CompileError
from sr8.config.settings import SR8Settings, build_settings_payload, resolve_compile_config
from sr8.io.exporters import load_artifact
from sr8.models.compile_config import CompileConfig
from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.source_intent import SourceType
from sr8.storage.load import load_by_id
from sr8.storage.workspace import SR8Workspace, init_workspace
from sr8.utils.paths import resolve_trusted_local_path

WINDOWS_DRIVE_PATH_RE = re.compile(r"^[a-zA-Z]:[\\/]")
ARTIFACT_SUFFIXES = {".json", ".yaml", ".yml"}
ARTIFACT_ID_RE = re.compile(r"^(art|drv)_[A-Za-z0-9]+$")
_RATE_LIMIT_LOCK = threading.Lock()
_RATE_LIMIT_STATE: dict[tuple[str, str], list[float]] = {}
_CONCURRENCY_LOCK = threading.Lock()
_ACTIVE_OPERATION_COUNT = 0


def get_settings() -> SR8Settings:
    return SR8Settings()


def get_settings_payload(settings: SR8Settings | None = None) -> dict[str, object]:
    return build_settings_payload(settings or get_settings())


def get_effective_settings_payload(settings: SR8Settings | None = None) -> dict[str, object]:
    payload = get_settings_payload(settings)
    configuration_error = payload.get("configuration_error")
    if isinstance(configuration_error, str):
        raise InvalidConfigurationError(configuration_error)
    return payload


def resolve_workspace(path: str | None = None) -> SR8Workspace:
    settings = get_settings()
    return init_workspace(path or settings.workspace_path)


def resolve_workspace_for_request(
    requested_path: str | None,
    settings: SR8Settings,
) -> SR8Workspace:
    configured = init_workspace(settings.workspace_path)
    if requested_path is None or requested_path.strip() == "":
        return configured
    requested = resolve_trusted_local_path(
        requested_path,
        extra_roots=[configured.root],
        must_exist=False,
    )
    if not settings.api_allow_workspace_override:
        if requested.resolve(strict=False) != configured.root.resolve(strict=False):
            raise WorkspaceAccessDeniedError(str(requested))
        return configured
    if not settings.api_allow_multi_tenant:
        try:
            relative = requested.resolve(strict=False).relative_to(
                configured.root.resolve(strict=False)
            )
        except ValueError as exc:
            raise WorkspaceAccessDeniedError(str(requested)) from exc
        requested = configured.root.resolve(strict=False) / relative
    return init_workspace(requested)


def validate_provider_name(provider: str | None) -> None:
    if provider is None:
        return
    if provider not in list_provider_names():
        raise InvalidProviderError(provider)


def resolve_compile_config_for_request(
    payload: CompileRequest,
    settings: SR8Settings | None = None,
) -> CompileConfig:
    active_settings = settings or get_settings()
    try:
        resolved = resolve_compile_config(
            active_settings,
            profile=payload.profile,
            target=payload.target,
            validate_target=payload.validate_target,
            mode=payload.mode,
            rule_only=payload.rule_only,
            assist_extract=payload.assist_extract,
            assist_provider=payload.assist_provider,
            assist_model=payload.assist_model,
            save_llm_trace=payload.save_llm_trace,
        )
    except ValueError as exc:
        raise InvalidConfigurationError(str(exc)) from exc
    validate_provider_name(resolved.assist_provider)
    return resolved


def _count_payload_nodes(value: object) -> int:
    if isinstance(value, Mapping):
        return 1 + sum(_count_payload_nodes(item) for item in value.values())
    if isinstance(value, list):
        return 1 + sum(_count_payload_nodes(item) for item in value)
    return 1


def enforce_compile_budget(payload: CompileRequest, settings: SR8Settings) -> None:
    source_text = payload.source_text or ""
    if len(source_text) > settings.api_max_source_chars:
        raise CompileBudgetExceededError(
            "Inline source text exceeds the configured API compile budget.",
            details={
                "limit": settings.api_max_source_chars,
                "actual": len(source_text),
            },
        )
    if payload.source_payload is not None:
        node_count = _count_payload_nodes(payload.source_payload)
        if node_count > settings.api_max_payload_nodes:
            raise CompileBudgetExceededError(
                "Structured payload exceeds the configured API compile budget.",
                details={
                    "limit": settings.api_max_payload_nodes,
                    "actual": node_count,
                },
            )


def resolve_request_identity(
    request: Request,
    *,
    settings: SR8Settings,
    exposure_class: RouteExposureClass,
    body_idempotency_key: str | None = None,
) -> RequestIdentity:
    header_idempotency = request.headers.get("x-idempotency-key")
    idempotency_key = body_idempotency_key or header_idempotency
    remote_host = request.client.host if request.client is not None else "local"
    actor_id = request.headers.get("x-sr8-actor") or "local-operator"
    if settings.api_auth_token and exposure_class != "safe":
        auth_header = request.headers.get("authorization", "")
        expected = f"Bearer {settings.api_auth_token}"
        if auth_header != expected:
            raise AuthenticationRequiredError()
        return RequestIdentity(
            actor_id=actor_id,
            auth_mode="bearer-token",
            idempotency_key=idempotency_key,
            remote_host=remote_host,
        )
    return RequestIdentity(
        actor_id=actor_id,
        auth_mode="trusted-local",
        idempotency_key=idempotency_key,
        remote_host=remote_host,
    )


def enforce_rate_limit(
    identity: RequestIdentity,
    *,
    route_id: str,
    settings: SR8Settings,
) -> None:
    limit = settings.api_rate_limit_requests
    if limit <= 0:
        return
    now = time.time()
    window = settings.api_rate_limit_window_seconds
    key = (identity.actor_id, route_id)
    with _RATE_LIMIT_LOCK:
        recent = [
            timestamp
            for timestamp in _RATE_LIMIT_STATE.get(key, [])
            if now - timestamp < window
        ]
        if len(recent) >= limit:
            retry_after = max(1, int(window - (now - recent[0])))
            _RATE_LIMIT_STATE[key] = recent
            raise RateLimitExceededError(route_id, retry_after)
        recent.append(now)
        _RATE_LIMIT_STATE[key] = recent


@contextmanager
def concurrency_guard(
    settings: SR8Settings,
    *,
    wait: bool = False,
) -> Iterator[None]:
    global _ACTIVE_OPERATION_COUNT
    while True:
        with _CONCURRENCY_LOCK:
            if _ACTIVE_OPERATION_COUNT < settings.api_max_concurrent_operations:
                _ACTIVE_OPERATION_COUNT += 1
                break
        if not wait:
            raise ConcurrencyLimitExceededError()
        time.sleep(0.01)
    try:
        yield
    finally:
        with _CONCURRENCY_LOCK:
            _ACTIVE_OPERATION_COUNT -= 1


def resolve_compile_source(
    payload: CompileRequest,
) -> tuple[str | Mapping[str, object], SourceType | None]:
    source_type = payload.source_type
    if payload.source_payload is not None:
        return payload.source_payload, source_type
    source_text = payload.source_text or ""
    if looks_like_disallowed_api_path(source_text):
        raise PathInputDisallowedError(source_text)
    return source_text, source_type


def map_compile_error(exc: Exception) -> SR8CompileError | None:
    if isinstance(exc, SR8CompileError):
        return exc
    return None


def load_artifact_for_api(path: str | Path) -> IntentArtifact:
    try:
        artifact_path = resolve_trusted_local_path(path, must_exist=True)
    except FileNotFoundError as exc:
        raise ArtifactNotFoundError(str(path)) from exc
    except ValueError as exc:
        raise InvalidArtifactReferenceError(str(path), str(exc)) from exc
    try:
        return load_artifact(artifact_path)
    except UnicodeDecodeError as exc:
        raise UnsupportedArtifactContentError(str(artifact_path), "binary_or_non_utf8") from exc
    except json.JSONDecodeError as exc:
        raise InvalidArtifactPayloadError(str(artifact_path), "invalid_json") from exc
    except yaml.YAMLError as exc:
        raise InvalidArtifactPayloadError(str(artifact_path), "invalid_yaml") from exc
    except ValidationError as exc:
        raise InvalidArtifactPayloadError(str(artifact_path), "schema_validation_failed") from exc
    except ValueError as exc:
        reason = "unsupported_extension"
        if "object/map" in str(exc):
            reason = "artifact_payload_not_object"
        raise InvalidArtifactPayloadError(str(artifact_path), reason) from exc


def resolve_canonical_artifact_for_api(
    value: str,
    workspace_path: str,
) -> tuple[IntentArtifact, str]:
    try:
        candidate = resolve_trusted_local_path(value, must_exist=True, extra_roots=[workspace_path])
    except FileNotFoundError:
        candidate = None
    except ValueError as exc:
        raise InvalidArtifactReferenceError(value, str(exc)) from exc
    if candidate is not None:
        artifact = load_artifact_for_api(candidate)
        return artifact, str(candidate)
    if looks_like_artifact_reference(value):
        raise ArtifactNotFoundError(value)

    try:
        loaded = load_by_id(resolve_workspace(workspace_path), value)
    except ValueError as exc:
        raise ArtifactNotFoundError(value) from exc
    if isinstance(loaded, DerivativeArtifact):
        msg = f"Identifier '{value}' resolves to a derivative artifact, not canonical."
        raise InvalidArtifactReferenceError(value, msg)
    return loaded, value


def resolve_inspect_artifact_for_api(
    value: str,
    workspace_path: str,
) -> tuple[IntentArtifact, str]:
    stripped = value.strip()
    try:
        candidate = resolve_trusted_local_path(
            stripped,
            must_exist=True,
            extra_roots=[workspace_path],
        )
    except FileNotFoundError:
        candidate = None
    except ValueError as exc:
        raise InvalidInspectTargetError(f"{stripped}: {exc}") from exc
    if candidate is not None and candidate.suffix.lower() in ARTIFACT_SUFFIXES:
        artifact = load_artifact_for_api(candidate)
        return artifact, str(candidate)
    if ARTIFACT_ID_RE.match(stripped):
        return resolve_canonical_artifact_for_api(stripped, workspace_path)
    raise InvalidInspectTargetError(stripped)


def looks_like_disallowed_api_path(value: str) -> bool:
    stripped = value.strip()
    if not stripped or "\n" in stripped or "\r" in stripped:
        return False
    if WINDOWS_DRIVE_PATH_RE.match(stripped):
        return True
    if (
        stripped.startswith("\\\\")
        or stripped.startswith("/")
        or stripped.startswith("~/")
        or stripped.startswith("~\\")
    ):
        return True
    try:
        resolve_trusted_local_path(stripped, must_exist=True)
        return True
    except (OSError, ValueError, FileNotFoundError):
        return False


def looks_like_artifact_reference(value: str) -> bool:
    stripped = value.strip()
    if not stripped or "\n" in stripped or "\r" in stripped:
        return False
    suffix = Path(stripped).suffix.lower()
    return suffix in ARTIFACT_SUFFIXES or looks_like_disallowed_api_path(stripped)
