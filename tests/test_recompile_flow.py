from pathlib import Path

from typer.testing import CliRunner

from sr8.cli import app
from sr8.compiler import compile_intent
from sr8.io.exporters import load_artifact

runner = CliRunner()


def test_cli_recompile_roundtrip(tmp_path: Path) -> None:
    source_artifact = load_artifact("tests/fixtures/compiled_prd_artifact.json")
    src_path = tmp_path / "base.json"
    src_path.write_text(source_artifact.model_dump_json(indent=2), encoding="utf-8")

    out_dir = tmp_path / "out"
    result = runner.invoke(
        app,
        [
            "recompile",
            str(src_path),
            "--profile",
            "code_task_graph",
            "--out",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    assert (out_dir / "latest.json").exists()


def test_compile_accepts_artifact_instance_for_recompile() -> None:
    source_artifact = load_artifact("tests/fixtures/compiled_prd_artifact.json")

    rebuilt = compile_intent(source_artifact).artifact

    assert rebuilt.source.source_hash == source_artifact.source.source_hash
    assert rebuilt.lineage.parent_artifact_ids[-1] == source_artifact.artifact_id
