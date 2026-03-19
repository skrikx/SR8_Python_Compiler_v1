from __future__ import annotations

from typing import cast

from fastapi import APIRouter

from sr8.api.schemas import CompileRequest, TransformRequest, ValidateRequest
from sr8.compiler import CompileConfig, compile_intent
from sr8.io.exporters import load_artifact
from sr8.models.source_intent import SourceType
from sr8.transform.engine import transform_artifact
from sr8.validate.engine import validate_artifact

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/compile")
def compile_endpoint(payload: CompileRequest) -> dict[str, object]:
    source_type = cast(SourceType | None, payload.source_type)
    result = compile_intent(
        source=payload.source,
        source_type=source_type,
        config=CompileConfig(profile=payload.profile),
    )
    return {
        "artifact": result.artifact.model_dump(mode="json"),
        "receipt": result.receipt.model_dump(mode="json"),
    }


@router.post("/validate")
def validate_endpoint(payload: ValidateRequest) -> dict[str, object]:
    artifact = load_artifact(payload.artifact_path)
    report = validate_artifact(artifact, profile_name=payload.profile)
    return report.model_dump(mode="json")


@router.post("/transform")
def transform_endpoint(payload: TransformRequest) -> dict[str, object]:
    artifact = load_artifact(payload.artifact_path)
    result = transform_artifact(artifact, payload.target)
    return result.derivative.model_dump(mode="json")
