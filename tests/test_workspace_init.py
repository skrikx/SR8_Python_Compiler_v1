from pathlib import Path

from sr8.storage.workspace import init_workspace


def test_workspace_init_creates_required_directories(tmp_path: Path) -> None:
    root = tmp_path / ".sr8"
    workspace = init_workspace(root)

    assert workspace.canonical_dir.exists()
    assert workspace.derivative_dir.exists()
    assert workspace.compile_receipts_dir.exists()
    assert workspace.transform_receipts_dir.exists()
    assert workspace.index_dir.exists()
    assert workspace.tmp_dir.exists()
    assert workspace.catalog_path.exists()
