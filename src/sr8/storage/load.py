from __future__ import annotations

import json
from pathlib import Path

from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.intent_artifact import IntentArtifact
from sr8.storage.index import resolve_record
from sr8.storage.workspace import SR8Workspace


def load_canonical(path: str | Path) -> IntentArtifact:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return IntentArtifact.model_validate(payload)


def load_derivative(path: str | Path) -> DerivativeArtifact:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return DerivativeArtifact.model_validate(payload)


def load_by_id(workspace: SR8Workspace, identifier: str) -> IntentArtifact | DerivativeArtifact:
    record = resolve_record(workspace, identifier)
    if record.artifact_kind == "canonical":
        return load_canonical(record.file_path)
    return load_derivative(record.file_path)
