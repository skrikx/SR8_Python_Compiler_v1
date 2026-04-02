from __future__ import annotations

from pathlib import Path

from sr8.io.exporters import artifact_to_json, artifact_to_yaml
from sr8.models.intent_artifact import IntentArtifact
from sr8.utils.paths import resolve_trusted_local_path


def write_artifact(
    artifact: IntentArtifact,
    out_dir: str | Path,
    export_format: str = "json",
) -> tuple[Path, Path]:
    output_dir = resolve_trusted_local_path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fmt = export_format.lower()
    if fmt not in {"json", "yaml"}:
        msg = f"Unsupported export format '{export_format}'."
        raise ValueError(msg)

    payload = artifact_to_json(artifact) if fmt == "json" else artifact_to_yaml(artifact)
    extension = "json" if fmt == "json" else "yaml"
    artifact_path = output_dir / f"{artifact.artifact_id}.{extension}"
    latest_path = output_dir / f"latest.{extension}"
    artifact_path.write_text(payload, encoding="utf-8")
    latest_path.write_text(payload, encoding="utf-8")
    return artifact_path, latest_path
