from __future__ import annotations

from pathlib import Path

from sr8.models.base import utc_now
from sr8.models.derivative_artifact import DerivativeArtifact, DerivativeLineage
from sr8.models.intent_artifact import IntentArtifact
from sr8.profiles.registry import get_profile
from sr8.transform.registry import get_transform_target
from sr8.transform.types import TransformResult
from sr8.utils.hash import stable_text_hash


def _build_derivative_id(parent_artifact_id: str, target: str, content: str) -> str:
    digest = stable_text_hash(f"{parent_artifact_id}:{target}:{content}")
    return f"drv_{digest[:20]}"


def transform_artifact(artifact: IntentArtifact, target: str) -> TransformResult:
    spec = get_transform_target(target)
    profile = get_profile(artifact.profile)

    if artifact.profile not in spec.compatible_profiles:
        msg = (
            f"Transform target '{target}' is incompatible with profile '{artifact.profile}'. "
            f"Supported profiles: {', '.join(spec.compatible_profiles)}"
        )
        raise ValueError(msg)
    if not profile.supports_target(target):
        msg = (
            f"Profile '{artifact.profile}' does not support target '{target}'. "
            f"Supported targets: {', '.join(profile.supported_transform_targets)}"
        )
        raise ValueError(msg)

    rendered_content = spec.renderer(artifact)
    derivative_id = _build_derivative_id(artifact.artifact_id, target, rendered_content)
    derivative = DerivativeArtifact(
        derivative_id=derivative_id,
        parent_artifact_id=artifact.artifact_id,
        parent_artifact_version=artifact.artifact_version,
        transform_target=target,
        profile=artifact.profile,
        created_at=utc_now(),
        content=rendered_content,
        lineage=DerivativeLineage(
            parent_source_hash=artifact.source.source_hash,
            parent_compile_run_id=artifact.lineage.compile_run_id,
            parent_lineage_steps=[step.stage for step in artifact.lineage.steps],
        ),
        metadata={
            "renderer_version": "w04.v1",
            "transform_target": target,
            "parent_profile": artifact.profile,
        },
    )
    return TransformResult(derivative=derivative, target=spec)


def summarize_transform(derivative: DerivativeArtifact) -> dict[str, object]:
    return {
        "derivative_id": derivative.derivative_id,
        "parent_artifact_id": derivative.parent_artifact_id,
        "transform_target": derivative.transform_target,
        "profile": derivative.profile,
    }


def write_derivative(
    derivative: DerivativeArtifact,
    out_dir: str | Path,
) -> tuple[Path, Path]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    derivative_path = output_dir / f"{derivative.derivative_id}.md"
    latest_path = output_dir / "latest_transform.md"
    derivative_path.write_text(derivative.content, encoding="utf-8")
    latest_path.write_text(derivative.content, encoding="utf-8")
    return derivative_path, latest_path
