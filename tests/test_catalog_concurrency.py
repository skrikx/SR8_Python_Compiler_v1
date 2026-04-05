import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from sr8.compiler import CompileConfig, compile_intent
from sr8.storage.catalog import list_catalog
from sr8.storage.save import save_canonical_artifact
from sr8.storage.workspace import init_workspace


def _save_parallel_artifact(workspace_root: Path, index: int) -> str:
    workspace = init_workspace(workspace_root)
    result = compile_intent(
        f"Objective: Parallel save {index}\nScope:\n- item {index}\n",
        config=CompileConfig(profile="generic", extraction_adapter="rule_based"),
    )
    _, _, record = save_canonical_artifact(workspace, result.artifact)
    return record.record_id


def test_catalog_survives_parallel_writes(tmp_path: Path) -> None:
    workspace = init_workspace(tmp_path / ".sr8")

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [
            executor.submit(_save_parallel_artifact, workspace.root, index)
            for index in range(80)
        ]
        record_ids = [future.result() for future in futures]

    payload = json.loads(workspace.catalog_path.read_text(encoding="utf-8"))
    records = list_catalog(workspace)

    assert len(record_ids) == 80
    assert len(payload["records"]) == 80
    assert len(records) == 80
    assert len({record.record_id for record in records}) == 80
