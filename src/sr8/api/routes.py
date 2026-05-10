from __future__ import annotations

import json
import threading
from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from sr8.adapters import list_provider_descriptors, probe_provider, probe_providers
from sr8.api.dependencies import (
    concurrency_guard,
    enforce_compile_budget,
    enforce_rate_limit,
    get_effective_settings_payload,
    get_settings,
    get_settings_payload,
    load_artifact_for_api,
    resolve_canonical_artifact_for_api,
    resolve_compile_config_for_request,
    resolve_compile_source,
    resolve_inspect_artifact_for_api,
    resolve_request_identity,
    resolve_workspace,
    resolve_workspace_for_request,
    validate_provider_name,
)
from sr8.api.errors import (
    ArtifactNotFoundError,
    AsyncJobNotFoundError,
    AsyncJobsDisabledError,
    IdempotencyConflictError,
    InvalidRequestError,
)
from sr8.api.schemas import (
    ArtifactDetailResponse,
    ArtifactsResponse,
    BenchmarkRunRequest,
    BenchmarkRunResponse,
    BenchmarkSuitesResponse,
    CompileRequest,
    CompileResponse,
    DiffRequest,
    HealthResponse,
    InspectRequest,
    InspectResponse,
    JobResponse,
    LintRequest,
    ProvidersProbeResponse,
    ProvidersResponse,
    ReceiptsResponse,
    ReportEnvelope,
    RouteContract,
    SettingsResponse,
    StatusResponse,
    TransformRequest,
    ValidateRequest,
)
from sr8.compiler import SR8CompileError, compile_intent
from sr8.diff.engine import semantic_diff
from sr8.eval import list_available_suites, run_benchmark_suite
from sr8.frontdoor import chat_compile
from sr8.frontdoor.command_parser import parse_chat_invocation
from sr8.lint.engine import lint_artifact
from sr8.models.async_job import AsyncJobError, AsyncJobRecord
from sr8.models.base import utc_now
from sr8.storage.catalog import list_catalog, show_catalog_record
from sr8.storage.jobs import create_or_reuse_job, load_job, save_job
from sr8.storage.load import load_by_id
from sr8.transform.engine import transform_artifact
from sr8.utils.hash import stable_object_hash
from sr8.validate.engine import validate_artifact

router = APIRouter()
_COMPILE_EXECUTOR = ThreadPoolExecutor(max_workers=8, thread_name_prefix="sr8-api-compile")
_SUBMITTED_JOBS: set[str] = set()
_SUBMITTED_JOBS_LOCK = threading.Lock()

ROUTE_CONTRACTS: dict[str, RouteContract] = {
    "health": RouteContract(
        route_id="health",
        exposure_class="safe",
        path_policy="no-local-paths",
        summary="Lightweight health status with no workspace disclosure.",
    ),
    "status": RouteContract(
        route_id="status",
        exposure_class="trusted-local",
        path_policy="workspace-summary-only",
        summary="Operator runtime status for trusted-local use.",
    ),
    "providers": RouteContract(
        route_id="providers",
        exposure_class="safe",
        path_policy="no-local-paths",
        summary="Provider descriptor listing without workspace reads.",
    ),
    "providers_probe": RouteContract(
        route_id="providers_probe",
        exposure_class="safe",
        path_policy="no-local-paths",
        summary="Provider readiness probe without artifact disclosure.",
    ),
    "settings": RouteContract(
        route_id="settings",
        exposure_class="trusted-local",
        path_policy="runtime-config-only",
        summary="Trusted-local runtime configuration surface.",
    ),
    "artifacts": RouteContract(
        route_id="artifacts",
        exposure_class="trusted-local",
        path_policy="workspace-index-only",
        summary="Trusted-local artifact index listing.",
    ),
    "artifact_detail": RouteContract(
        route_id="artifact_detail",
        exposure_class="trusted-local",
        path_policy="workspace-artifact-only",
        summary="Trusted-local artifact record and payload inspection.",
    ),
    "receipts": RouteContract(
        route_id="receipts",
        exposure_class="trusted-local",
        path_policy="workspace-receipts-only",
        summary="Trusted-local receipt listing.",
    ),
    "compile": RouteContract(
        route_id="compile",
        exposure_class="deliberate-exposure",
        path_policy="inline-source-or-structured-payload-only",
        summary="Compile inline intent without reading caller-supplied local paths.",
    ),
    "jobs": RouteContract(
        route_id="jobs",
        exposure_class="deliberate-exposure",
        path_policy="job-record-only",
        summary="Poll async compile jobs created by deliberate compile requests.",
    ),
    "inspect": RouteContract(
        route_id="inspect",
        exposure_class="trusted-local",
        path_policy="trusted-local-artifact-only",
        summary="Inspect trusted-local artifacts only. No inline compile path.",
    ),
    "validate": RouteContract(
        route_id="validate",
        exposure_class="trusted-local",
        path_policy="trusted-local-artifact-only",
        summary="Validate a trusted-local canonical artifact.",
    ),
    "transform": RouteContract(
        route_id="transform",
        exposure_class="trusted-local",
        path_policy="trusted-local-artifact-only",
        summary="Transform a trusted-local canonical artifact.",
    ),
    "diff": RouteContract(
        route_id="diff",
        exposure_class="trusted-local",
        path_policy="trusted-local-artifact-or-id-only",
        summary="Diff trusted-local canonical artifacts.",
    ),
    "lint": RouteContract(
        route_id="lint",
        exposure_class="trusted-local",
        path_policy="trusted-local-artifact-or-id-only",
        summary="Lint trusted-local canonical artifacts.",
    ),
    "benchmark_suites": RouteContract(
        route_id="benchmark_suites",
        exposure_class="trusted-local",
        path_policy="no-local-paths",
        summary="Trusted-local benchmark suite listing.",
    ),
    "benchmark_run": RouteContract(
        route_id="benchmark_run",
        exposure_class="trusted-local",
        path_policy="trusted-local-output-only",
        summary="Trusted-local benchmark execution.",
    ),
}


def _route_contract_payload(route_name: str) -> dict[str, object]:
    return ROUTE_CONTRACTS[route_name].model_dump(mode="json")


def _route_openapi_extra(route_name: str) -> dict[str, object]:
    return {"x-sr8-route-contract": _route_contract_payload(route_name)}


def _route_response(route_name: str, payload: dict[str, object]) -> dict[str, object]:
    return {"route_contract": _route_contract_payload(route_name), **payload}


def _read_receipt_dir(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    receipts: list[dict[str, object]] = []
    for file_path in sorted(path.glob("*.json")):
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            receipts.append(payload)
    return receipts


def _should_use_frontdoor(source_text: str) -> bool:
    parsed = parse_chat_invocation(source_text)
    return parsed.raw.strip().lower().startswith(("compile:", "resume:")) or (
        "<compiler_input_form" in parsed.raw.lower()
    )


def _raise_invalid_request(code: str, exc: Exception) -> None:
    if isinstance(exc, SR8CompileError):
        raise InvalidRequestError(exc.code, exc.message, exc.details) from exc
    raise InvalidRequestError(code, str(exc)) from exc


def _build_compile_payload(
    source: str | Mapping[str, object],
    *,
    compile_request: CompileRequest,
    identity_payload: dict[str, object],
) -> dict[str, object]:
    settings = get_settings()
    compile_config = resolve_compile_config_for_request(compile_request, settings)
    source_type = compile_request.source_type
    try:
        with concurrency_guard(settings, wait=compile_request.async_mode):
            if isinstance(source, str) and _should_use_frontdoor(source):
                frontdoor_result = chat_compile(source, config=compile_config)
                return _route_response(
                    "compile",
                    {
                        "frontdoor": frontdoor_result.model_dump(mode="json"),
                        "artifact": frontdoor_result.artifact.model_dump(mode="json")
                        if frontdoor_result.artifact
                        else None,
                        "receipt": frontdoor_result.receipt.model_dump(mode="json")
                        if frontdoor_result.receipt
                        else None,
                        "normalized_source": frontdoor_result.normalized_source.model_dump(
                            mode="json"
                        )
                        if frontdoor_result.normalized_source
                        else None,
                        "extracted_dimensions": frontdoor_result.extracted_dimensions.model_dump(
                            mode="json"
                        )
                        if frontdoor_result.extracted_dimensions
                        else None,
                        "target_validation": None,
                        "job": None,
                        "request_identity": identity_payload,
                        "replayed": False,
                    },
                )
            result = compile_intent(source=source, source_type=source_type, config=compile_config)
    except ValueError as exc:
        _raise_invalid_request("invalid_compile_request", exc)
    return _route_response(
        "compile",
        {
            "frontdoor": None,
            "artifact": result.artifact.model_dump(mode="json"),
            "receipt": result.receipt.model_dump(mode="json"),
            "normalized_source": result.normalized_source.model_dump(mode="json"),
            "extracted_dimensions": result.extracted_dimensions.model_dump(mode="json"),
            "target_validation": result.target_validation.model_dump(mode="json")
            if result.target_validation
            else None,
            "job": None,
            "request_identity": identity_payload,
            "replayed": False,
        },
    )


def _submit_compile_job(
    *,
    workspace_path: str,
    compile_request: CompileRequest,
    request_identity: dict[str, object],
    job: AsyncJobRecord,
) -> None:
    with _SUBMITTED_JOBS_LOCK:
        if job.job_id in _SUBMITTED_JOBS:
            return
        _SUBMITTED_JOBS.add(job.job_id)

    def _runner() -> None:
        workspace = resolve_workspace(workspace_path)
        running = job.model_copy(
            update={"status": "running", "attempts": job.attempts + 1}
        )
        running.started_at = running.started_at or running.created_at
        save_job(workspace, running)
        try:
            compile_payload = _build_compile_payload(
                compile_request.source_payload
                if compile_request.source_payload is not None
                else (compile_request.source_text or ""),
                compile_request=compile_request,
                identity_payload=request_identity,
            )
            completed = running.model_copy(
                update={
                    "status": "completed",
                    "result_payload": compile_payload,
                }
            )
            completed.completed_at = utc_now()
            save_job(workspace, completed)
        except Exception as exc:  # pragma: no cover - defensive async boundary
            code = "internal_error"
            details: dict[str, object] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            }
            message = "Internal server error."
            if isinstance(exc, InvalidRequestError):
                code = exc.code
                message = exc.message
                details = exc.details
            elif isinstance(exc, SR8CompileError):
                code = exc.code
                message = exc.message
                details = exc.details
            failed = running.model_copy(
                update={
                    "status": "failed",
                    "error": AsyncJobError(code=code, message=message, details=details),
                }
            )
            failed.completed_at = utc_now()
            save_job(workspace, failed)
        finally:
            with _SUBMITTED_JOBS_LOCK:
                _SUBMITTED_JOBS.discard(job.job_id)

    _COMPILE_EXECUTOR.submit(_runner)


@router.get(
    "/health",
    response_model=HealthResponse,
    openapi_extra=_route_openapi_extra("health"),
)
def health() -> dict[str, object]:
    return _route_response("health", {"status": "ok"})


@router.get(
    "/status",
    response_model=StatusResponse,
    openapi_extra=_route_openapi_extra("status"),
)
def status(request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["status"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    workspace = resolve_workspace(settings.workspace_path)
    settings_payload = get_settings_payload(settings)
    return _route_response(
        "status",
        {
            "status": "ok",
            "workspace_path": str(workspace.root),
            "default_profile": settings_payload["default_profile"],
            "extraction_adapter": settings_payload["extraction_adapter"],
            "providers": [result.model_dump(mode="json") for result in probe_providers()],
            "benchmark_suites": list_available_suites(),
        },
    )


@router.get(
    "/providers",
    response_model=ProvidersResponse,
    openapi_extra=_route_openapi_extra("providers"),
)
def providers_endpoint() -> dict[str, object]:
    providers = [descriptor.model_dump(mode="json") for descriptor in list_provider_descriptors()]
    return _route_response(
        "providers",
        {"providers": providers},
    )


@router.get(
    "/providers/probe",
    response_model=ProvidersProbeResponse,
    openapi_extra=_route_openapi_extra("providers_probe"),
)
def providers_probe_endpoint(provider: str | None = None) -> dict[str, object]:
    if provider is not None:
        validate_provider_name(provider)
        return _route_response(
            "providers_probe",
            {"result": probe_provider(provider).model_dump(mode="json"), "results": []},
        )
    results = [result.model_dump(mode="json") for result in probe_providers()]
    return _route_response(
        "providers_probe",
        {"result": None, "results": results},
    )


@router.get(
    "/settings",
    response_model=SettingsResponse,
    openapi_extra=_route_openapi_extra("settings"),
)
def settings_endpoint(request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["settings"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    return _route_response("settings", {"settings": get_effective_settings_payload()})


@router.get(
    "/artifacts",
    response_model=ArtifactsResponse,
    openapi_extra=_route_openapi_extra("artifacts"),
)
def artifacts_endpoint(
    request: Request,
    kind: str | None = None,
    profile: str | None = None,
) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["artifacts"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    if kind is not None and kind not in {"canonical", "derivative"}:
        raise InvalidRequestError("invalid_artifact_kind", "kind must be canonical or derivative")
    workspace = resolve_workspace()
    records = list_catalog(workspace, kind=kind, profile=profile)
    return _route_response(
        "artifacts",
        {"records": [record.model_dump(mode="json") for record in records]},
    )


@router.get(
    "/artifacts/{identifier}",
    response_model=ArtifactDetailResponse,
    openapi_extra=_route_openapi_extra("artifact_detail"),
)
def artifact_detail_endpoint(identifier: str, request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["artifact_detail"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    workspace = resolve_workspace()
    try:
        record = show_catalog_record(workspace, identifier)
        payload = load_by_id(workspace, identifier)
    except ValueError as exc:
        raise ArtifactNotFoundError(identifier) from exc
    return _route_response(
        "artifact_detail",
        {
            "record": record.model_dump(mode="json"),
            "payload": payload.model_dump(mode="json"),
        },
    )


@router.get(
    "/receipts",
    response_model=ReceiptsResponse,
    openapi_extra=_route_openapi_extra("receipts"),
)
def receipts_endpoint(request: Request, kind: str = "compile") -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["receipts"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    workspace = resolve_workspace()
    if kind == "compile":
        receipts = _read_receipt_dir(workspace.compile_receipts_dir)
    elif kind == "transform":
        receipts = _read_receipt_dir(workspace.transform_receipts_dir)
    else:
        raise InvalidRequestError("invalid_receipt_kind", "kind must be compile or transform")
    return _route_response("receipts", {"receipts": receipts})


@router.post(
    "/compile",
    response_model=CompileResponse,
    openapi_extra=_route_openapi_extra("compile"),
)
def compile_endpoint(payload: CompileRequest, request: Request) -> JSONResponse | dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["compile"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
        body_idempotency_key=payload.idempotency_key,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    enforce_compile_budget(payload, settings)
    workspace = resolve_workspace_for_request(payload.workspace_path, settings)
    source, _ = resolve_compile_source(payload)
    request_hash = stable_object_hash(
        {
            "source": source,
            "source_type": payload.source_type,
            "profile": payload.profile,
            "rule_only": payload.rule_only,
            "assist_provider": payload.assist_provider,
            "assist_model": payload.assist_model,
            "target": payload.target,
            "validate_target": payload.validate_target,
            "async_mode": payload.async_mode,
        }
    )
    try:
        job, reused = create_or_reuse_job(
            workspace,
            operation="compile",
            request_hash=request_hash,
            actor_id=identity.actor_id,
            idempotency_key=identity.idempotency_key,
        )
    except ValueError as exc:
        raise IdempotencyConflictError() from exc
    if payload.async_mode:
        if not settings.api_async_jobs_enabled:
            raise AsyncJobsDisabledError()
        if not reused:
            _submit_compile_job(
                workspace_path=str(workspace.root),
                compile_request=payload,
                request_identity=identity.model_dump(mode="json"),
                job=job,
            )
        response_payload = _route_response(
            "compile",
            {
                "frontdoor": None,
                "artifact": None,
                "receipt": None,
                "normalized_source": None,
                "extracted_dimensions": None,
                "target_validation": None,
                "job": job.model_dump(mode="json"),
                "request_identity": identity.model_dump(mode="json"),
                "replayed": reused,
            },
        )
        return JSONResponse(status_code=202, content=response_payload)
    if reused:
        if job.result_payload is not None:
            replayed_payload = dict(job.result_payload)
            replayed_payload["replayed"] = True
            replayed_payload["request_identity"] = identity.model_dump(mode="json")
            return replayed_payload
        if job.status in {"queued", "running"}:
            return JSONResponse(
                status_code=202,
                content=_route_response(
                    "compile",
                    {
                        "frontdoor": None,
                        "artifact": None,
                        "receipt": None,
                        "normalized_source": None,
                        "extracted_dimensions": None,
                        "target_validation": None,
                        "job": job.model_dump(mode="json"),
                        "request_identity": identity.model_dump(mode="json"),
                        "replayed": True,
                    },
                ),
            )
        if job.error is not None:
            raise InvalidRequestError(job.error.code, job.error.message, job.error.details)
    compile_payload = _build_compile_payload(
        source,
        compile_request=payload,
        identity_payload=identity.model_dump(mode="json"),
    )
    completed_job = job.model_copy(
        update={
            "status": "completed",
            "attempts": job.attempts + 1,
            "result_payload": compile_payload,
        }
    )
    completed_job.started_at = utc_now()
    completed_job.completed_at = completed_job.started_at
    save_job(workspace, completed_job)
    return compile_payload


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    openapi_extra=_route_openapi_extra("jobs"),
)
def job_detail_endpoint(job_id: str, request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["jobs"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    workspace = resolve_workspace()
    try:
        job = load_job(workspace, job_id)
    except ValueError as exc:
        raise AsyncJobNotFoundError(job_id) from exc
    return _route_response(
        "jobs",
        {
            "job": job.model_dump(mode="json"),
            "request_identity": identity.model_dump(mode="json"),
        },
    )


@router.post(
    "/inspect",
    response_model=InspectResponse,
    openapi_extra=_route_openapi_extra("inspect"),
)
def inspect_endpoint(payload: InspectRequest, request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["inspect"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    workspace = resolve_workspace_for_request(payload.workspace_path, settings)
    artifact, artifact_ref = resolve_inspect_artifact_for_api(payload.target, str(workspace.root))
    return _route_response(
        "inspect",
        {
            "artifact": artifact.model_dump(mode="json"),
            "artifact_ref": artifact_ref,
            "mode": "artifact",
        },
    )


@router.post(
    "/validate",
    response_model=ReportEnvelope,
    openapi_extra=_route_openapi_extra("validate"),
)
def validate_endpoint(payload: ValidateRequest, request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["validate"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    artifact = load_artifact_for_api(payload.artifact_path)
    report = validate_artifact(artifact, profile_name=payload.profile)
    return _route_response(
        "validate",
        {
            "request_identity": identity.model_dump(mode="json"),
            "payload": report.model_dump(mode="json"),
        },
    )


@router.post(
    "/transform",
    response_model=ReportEnvelope,
    openapi_extra=_route_openapi_extra("transform"),
)
def transform_endpoint(payload: TransformRequest, request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["transform"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    artifact = load_artifact_for_api(payload.artifact_path)
    try:
        result = transform_artifact(artifact, payload.target)
    except ValueError as exc:
        raise InvalidRequestError("invalid_transform_request", str(exc)) from exc
    return _route_response(
        "transform",
        {
            "request_identity": identity.model_dump(mode="json"),
            "payload": result.derivative.model_dump(mode="json"),
        },
    )


@router.post(
    "/diff",
    response_model=ReportEnvelope,
    openapi_extra=_route_openapi_extra("diff"),
)
def diff_endpoint(payload: DiffRequest, request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["diff"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    workspace = resolve_workspace_for_request(payload.workspace_path, settings)
    left_artifact, left_ref = resolve_canonical_artifact_for_api(
        payload.left,
        str(workspace.root),
    )
    right_artifact, right_ref = resolve_canonical_artifact_for_api(
        payload.right,
        str(workspace.root),
    )
    report = semantic_diff(
        left_artifact,
        right_artifact,
        left_ref=left_ref,
        right_ref=right_ref,
    )
    return _route_response(
        "diff",
        {
            "request_identity": identity.model_dump(mode="json"),
            "payload": report.model_dump(mode="json"),
        },
    )


@router.post(
    "/lint",
    response_model=ReportEnvelope,
    openapi_extra=_route_openapi_extra("lint"),
)
def lint_endpoint(payload: LintRequest, request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["lint"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    workspace = resolve_workspace_for_request(payload.workspace_path, settings)
    artifact, artifact_ref = resolve_canonical_artifact_for_api(
        payload.artifact_ref,
        str(workspace.root),
    )
    report = lint_artifact(artifact, artifact_ref=artifact_ref)
    return _route_response(
        "lint",
        {
            "request_identity": identity.model_dump(mode="json"),
            "payload": report.model_dump(mode="json"),
        },
    )


@router.get(
    "/benchmarks/suites",
    response_model=BenchmarkSuitesResponse,
    openapi_extra=_route_openapi_extra("benchmark_suites"),
)
def benchmark_suites_endpoint(request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["benchmark_suites"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    return _route_response("benchmark_suites", {"suites": list_available_suites()})


@router.post(
    "/benchmarks/run",
    response_model=BenchmarkRunResponse,
    openapi_extra=_route_openapi_extra("benchmark_run"),
)
def benchmark_run_endpoint(payload: BenchmarkRunRequest, request: Request) -> dict[str, object]:
    settings = get_settings()
    route = ROUTE_CONTRACTS["benchmark_run"]
    identity = resolve_request_identity(
        request,
        settings=settings,
        exposure_class=route.exposure_class,
    )
    enforce_rate_limit(identity, route_id=route.route_id, settings=settings)
    if payload.suite is not None and payload.suite not in list_available_suites():
        raise InvalidRequestError("invalid_benchmark_suite", f"Unknown suite '{payload.suite}'.")
    try:
        report = run_benchmark_suite(suite=payload.suite, out_dir=payload.out_dir)
    except ValueError as exc:
        raise InvalidRequestError("invalid_benchmark_request", str(exc)) from exc
    return _route_response("benchmark_run", {"payload": report.model_dump(mode="json")})
