from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import yaml

from sr8.models.intent_artifact import IntentArtifact
from sr8.utils.paths import resolve_trusted_local_path


def artifact_to_json(artifact: IntentArtifact) -> str:
    payload = artifact.model_dump(mode="json")
    return json.dumps(payload, indent=2, sort_keys=True)


def artifact_to_yaml(artifact: IntentArtifact) -> str:
    payload = artifact.model_dump(mode="json")
    dumped = yaml.safe_dump(payload, sort_keys=True, allow_unicode=False)
    return cast(str, dumped)


def load_artifact(path: str | Path) -> IntentArtifact:
    artifact_path = resolve_trusted_local_path(path, must_exist=True)
    content = artifact_path.read_text(encoding="utf-8")
    suffix = artifact_path.suffix.lower()
    if suffix == ".json":
        payload = json.loads(content)
    elif suffix in {".yaml", ".yml"}:
        payload = yaml.safe_load(content)
    else:
        msg = f"Unsupported artifact extension '{suffix}'. Use .json or .yaml."
        raise ValueError(msg)
    if not isinstance(payload, dict):
        msg = "Artifact payload must be an object/map."
        raise ValueError(msg)
    return IntentArtifact.model_validate(payload)
