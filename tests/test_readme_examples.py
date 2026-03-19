from pathlib import Path

from typer.testing import CliRunner

from sr8.cli import app

runner = CliRunner()


def test_readme_example_commands_work(tmp_path: Path) -> None:
    workspace = tmp_path / ".sr8"
    assert runner.invoke(app, ["init", "--path", str(workspace)]).exit_code == 0

    compile_result = runner.invoke(
        app,
        [
            "compile",
            "examples/product_prd.md",
            "--profile",
            "prd",
            "--out",
            str(workspace / "artifacts" / "canonical"),
        ],
    )
    assert compile_result.exit_code == 0

    transform_result = runner.invoke(
        app,
        [
            "transform",
            str(workspace / "artifacts" / "canonical" / "latest.json"),
            "--to",
            "markdown_prd",
            "--out",
            str(workspace / "artifacts" / "derivative"),
        ],
    )
    assert transform_result.exit_code == 0

    lint_result = runner.invoke(
        app,
        ["lint", str(workspace / "artifacts" / "canonical" / "latest.json")],
    )
    assert lint_result.exit_code == 0
    assert "Lint Report:" in lint_result.stdout
