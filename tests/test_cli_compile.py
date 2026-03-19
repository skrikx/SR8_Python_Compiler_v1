from pathlib import Path

from typer.testing import CliRunner

from sr8.cli import app

runner = CliRunner()


def test_cli_compile_writes_json_artifact(tmp_path: Path) -> None:
    fixture = Path("tests/fixtures/product_prd.md")
    out_dir = tmp_path / "artifacts"

    result = runner.invoke(
        app,
        [
            "compile",
            str(fixture),
            "--profile",
            "prd",
            "--out",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    assert (out_dir / "latest.json").exists()
    assert "Validation:" in result.stdout
