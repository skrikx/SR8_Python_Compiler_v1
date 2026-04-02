from __future__ import annotations

import json
from pathlib import Path


class SR8Workspace:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    @property
    def canonical_dir(self) -> Path:
        return self.root / "artifacts" / "canonical"

    @property
    def derivative_dir(self) -> Path:
        return self.root / "artifacts" / "derivative"

    @property
    def compile_receipts_dir(self) -> Path:
        return self.root / "receipts" / "compile"

    @property
    def transform_receipts_dir(self) -> Path:
        return self.root / "receipts" / "transform"

    @property
    def index_dir(self) -> Path:
        return self.root / "index"

    @property
    def tmp_dir(self) -> Path:
        return self.root / "tmp"

    @property
    def catalog_path(self) -> Path:
        return self.index_dir / "catalog.json"

    @property
    def catalog_lock_path(self) -> Path:
        return self.index_dir / "catalog.lock"

    def initialize(self) -> None:
        for directory in (
            self.canonical_dir,
            self.derivative_dir,
            self.compile_receipts_dir,
            self.transform_receipts_dir,
            self.index_dir,
            self.tmp_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        if not self.catalog_path.exists():
            self.catalog_path.write_text(json.dumps({"records": []}, indent=2), encoding="utf-8")


def init_workspace(path: str | Path = ".sr8") -> SR8Workspace:
    workspace = SR8Workspace(path)
    workspace.initialize()
    return workspace
