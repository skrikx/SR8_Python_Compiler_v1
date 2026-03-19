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

    latest_artifact = str(workspace / "artifacts" / "canonical" / "latest.json")

    validate_result = runner.invoke(
        app,
        ["validate", latest_artifact],
    )
    assert validate_result.exit_code == 0
    assert "Validation:" in validate_result.stdout

    transform_result = runner.invoke(
        app,
        [
            "transform",
            latest_artifact,
            "--to",
            "markdown_prd",
            "--out",
            str(workspace / "artifacts" / "derivative"),
        ],
    )
    assert transform_result.exit_code == 0

    lint_result = runner.invoke(
        app,
        ["lint", latest_artifact],
    )
    assert lint_result.exit_code == 0
    assert "Lint Report:" in lint_result.stdout

    diff_result = runner.invoke(
        app,
        [
            "diff",
            "tests/fixtures/diff/base_artifact.json",
            "tests/fixtures/diff/changed_artifact.json",
        ],
    )
    assert diff_result.exit_code == 0
    assert "Diff Report:" in diff_result.stdout

    list_result = runner.invoke(app, ["list", "--path", str(workspace)])
    assert list_result.exit_code == 0
    assert "canonical" in list_result.stdout
