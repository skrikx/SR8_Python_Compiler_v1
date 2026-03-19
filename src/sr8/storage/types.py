from __future__ import annotations

from pathlib import Path
from typing import Literal

from sr8.models.base import SR8Model

ArtifactKind = Literal["canonical", "derivative"]


class StorageSettings(SR8Model):
    workspace_root: Path
    allow_overwrite: bool = False
