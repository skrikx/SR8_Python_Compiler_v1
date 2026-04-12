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
    assert "Compile Kind:" in result.stdout
    assert "Validation:" in result.stdout


def test_cli_compile_uses_settings_default_profile(monkeypatch, tmp_path: Path) -> None:
    fixture = tmp_path / "inline.md"
    fixture.write_text("Objective: Ship plan\nScope:\n- Step 1\n", encoding="utf-8")
    out_dir = tmp_path / "artifacts"
    monkeypatch.setenv("SR8_DEFAULT_PROFILE", "plan")

    result = runner.invoke(
        app,
        [
            "compile",
            str(fixture),
            "--out",
            str(out_dir),
        ],
    )

    assert result.exit_code == 0
    assert "Profile: plan" in result.stdout
