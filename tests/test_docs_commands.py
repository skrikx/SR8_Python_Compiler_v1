from pathlib import Path

from typer.testing import CliRunner

from sr8.cli import app
from sr8.io.exporters import load_artifact

runner = CliRunner()


def test_docs_command_flow(tmp_path: Path) -> None:
    workspace = tmp_path / ".sr8"
    assert runner.invoke(app, ["init", "--path", str(workspace)]).exit_code == 0

    compile_result = runner.invoke(
        app,
        [
            "compile",
            "examples/founder_ask.md",
            "--profile",
            "generic",
            "--out",
            str(workspace / "artifacts" / "canonical"),
        ],
    )
    assert compile_result.exit_code == 0
    assert "Artifact ID:" in compile_result.stdout

    latest_artifact = workspace / "artifacts" / "canonical" / "latest.json"
    assert latest_artifact.exists()

    inspect_result = runner.invoke(app, ["inspect", str(latest_artifact)])
    assert inspect_result.exit_code == 0
    assert "Profile:" in inspect_result.stdout

    validate_result = runner.invoke(app, ["validate", str(latest_artifact)])
    assert validate_result.exit_code == 0
    assert "Validation:" in validate_result.stdout

    transform_result = runner.invoke(
        app,
        [
            "transform",
            str(latest_artifact),
            "--to",
            "markdown_plan",
            "--out",
            str(workspace / "artifacts" / "derivative"),
        ],
    )
    assert transform_result.exit_code == 0

    lint_result = runner.invoke(app, ["lint", str(latest_artifact)])
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

    artifact = load_artifact(latest_artifact)
    show_result = runner.invoke(app, ["show", artifact.artifact_id, "--path", str(workspace)])
    assert show_result.exit_code == 0
    assert "Record:" in show_result.stdout


def test_docs_examples_assets_exist() -> None:
    assert Path("docs/index.md").exists()
    assert Path("docs/examples.md").exists()
    assert Path("docs/install.md").exists()
    assert Path("examples/outputs/canonical_repo_audit.json").exists()
    assert Path("examples/outputs/diff_summary.txt").exists()
    assert Path("examples/outputs/lint_report.txt").exists()
