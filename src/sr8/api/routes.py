from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter

from sr8.adapters import list_provider_descriptors, probe_provider, probe_providers
from sr8.api.dependencies import (
    get_settings,
    get_settings_payload,
    load_artifact_for_api,
    resolve_canonical_artifact_for_api,
    resolve_compile_config_for_request,
    resolve_compile_source,
    resolve_workspace,
    validate_provider_name,
)
from sr8.api.errors import ArtifactNotFoundError, InvalidRequestError
from sr8.api.schemas import (
    BenchmarkRunRequest,
    CompileRequest,
    DiffRequest,
    InspectRequest,
    LintRequest,
    TransformRequest,
    ValidateRequest,
)
from sr8.compiler import compile_intent
from sr8.diff.engine import semantic_diff
from sr8.eval import list_available_suites, run_benchmark_suite
from sr8.lint.engine import lint_artifact
from sr8.storage.catalog import list_catalog, show_catalog_record
from sr8.storage.load import load_by_id
from sr8.transform.engine import transform_artifact
from sr8.validate.engine import validate_artifact

router = APIRouter()


def _read_receipt_dir(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []
    receipts: list[dict[str, object]] = []
    for file_path in sorted(path.glob("*.json")):
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            receipts.append(payload)
    return receipts


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/status")
def status() -> dict[str, object]:
    settings = get_settings()
    workspace = resolve_workspace(settings.workspace_path)
    settings_payload = get_settings_payload(settings)
    return {
        "status": "ok",
        "workspace_path": str(workspace.root),
        "default_profile": settings_payload["default_profile"],
        "extraction_adapter": settings_payload["extraction_adapter"],
        "providers": [result.model_dump(mode="json") for result in probe_providers()],
        "benchmark_suites": list_available_suites(),
    }


@router.get("/providers")
def providers_endpoint() -> list[dict[str, object]]:
    return [descriptor.model_dump(mode="json") for descriptor in list_provider_descriptors()]


@router.get("/providers/probe")
def providers_probe_endpoint(provider: str | None = None) -> dict[str, object]:
    if provider is not None:
        validate_provider_name(provider)
        return probe_provider(provider).model_dump(mode="json")
    return {"results": [result.model_dump(mode="json") for result in probe_providers()]}


@router.get("/settings")
def settings_endpoint() -> dict[str, object]:
    return get_settings_payload()


@router.get("/artifacts")
def artifacts_endpoint(kind: str | None = None, profile: str | None = None) -> dict[str, object]:
    workspace = resolve_workspace()
    records = list_catalog(workspace, kind=kind, profile=profile)
    return {"records": [record.model_dump(mode="json") for record in records]}


@router.get("/artifacts/{identifier}")
def artifact_detail_endpoint(identifier: str) -> dict[str, object]:
    workspace = resolve_workspace()
    try:
        record = show_catalog_record(workspace, identifier)
        payload = load_by_id(workspace, identifier)
    except ValueError as exc:
        raise ArtifactNotFoundError(identifier) from exc
    return {
        "record": record.model_dump(mode="json"),
        "payload": payload.model_dump(mode="json"),
    }


@router.get("/receipts")
def receipts_endpoint(kind: str = "compile") -> dict[str, object]:
    workspace = resolve_workspace()
    if kind == "compile":
        receipts = _read_receipt_dir(workspace.compile_receipts_dir)
    elif kind == "transform":
        receipts = _read_receipt_dir(workspace.transform_receipts_dir)
    else:
        raise InvalidRequestError("invalid_receipt_kind", "kind must be compile or transform")
    return {"receipts": receipts}


@router.post("/compile")
def compile_endpoint(payload: CompileRequest) -> dict[str, object]:
    settings = get_settings()
    source, source_type = resolve_compile_source(payload)
    compile_config = resolve_compile_config_for_request(payload, settings)
    result = compile_intent(
        source=source,
        source_type=source_type,
        config=compile_config,
    )
    return {
        "artifact": result.artifact.model_dump(mode="json"),
        "receipt": result.receipt.model_dump(mode="json"),
        "normalized_source": result.normalized_source.model_dump(mode="json"),
        "extracted_dimensions": result.extracted_dimensions.model_dump(mode="json"),
    }


@router.post("/inspect")
def inspect_endpoint(payload: InspectRequest) -> dict[str, object]:
    candidate = Path(payload.target)
    if candidate.suffix.lower() in {".json", ".yaml", ".yml"} or candidate.exists():
        artifact = load_artifact_for_api(candidate)
        return {"artifact": artifact.model_dump(mode="json"), "mode": "artifact"}
    settings = get_settings()
    result = compile_intent(
        source=payload.target,
        config=resolve_compile_config_for_request(
            CompileRequest(source_text=payload.target, profile=settings.default_profile),
            settings,
        ),
    )
    return {
        "artifact": result.artifact.model_dump(mode="json"),
        "receipt": result.receipt.model_dump(mode="json"),
        "mode": "compiled_source",
    }


@router.post("/validate")
def validate_endpoint(payload: ValidateRequest) -> dict[str, object]:
    artifact = load_artifact_for_api(payload.artifact_path)
    report = validate_artifact(artifact, profile_name=payload.profile)
    return report.model_dump(mode="json")


@router.post("/transform")
def transform_endpoint(payload: TransformRequest) -> dict[str, object]:
    artifact = load_artifact_for_api(payload.artifact_path)
    result = transform_artifact(artifact, payload.target)
    return result.derivative.model_dump(mode="json")


@router.post("/diff")
def diff_endpoint(payload: DiffRequest) -> dict[str, object]:
    left_artifact, left_ref = resolve_canonical_artifact_for_api(
        payload.left,
        payload.workspace_path,
    )
    right_artifact, right_ref = resolve_canonical_artifact_for_api(
        payload.right,
        payload.workspace_path,
    )
    return semantic_diff(
        left_artifact,
        right_artifact,
        left_ref=left_ref,
        right_ref=right_ref,
    ).model_dump(mode="json")


@router.post("/lint")
def lint_endpoint(payload: LintRequest) -> dict[str, object]:
    artifact, artifact_ref = resolve_canonical_artifact_for_api(
        payload.artifact_ref,
        payload.workspace_path,
    )
    return lint_artifact(artifact, artifact_ref=artifact_ref).model_dump(mode="json")


@router.get("/benchmarks/suites")
def benchmark_suites_endpoint() -> dict[str, object]:
    return {"suites": list_available_suites()}


@router.post("/benchmarks/run")
def benchmark_run_endpoint(payload: BenchmarkRunRequest) -> dict[str, object]:
    report = run_benchmark_suite(suite=payload.suite, out_dir=payload.out_dir)
    return report.model_dump(mode="json")
