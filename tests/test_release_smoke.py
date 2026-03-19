from typer.testing import CliRunner

from sr8.cli import app
from sr8.version import __version__

runner = CliRunner()


def test_cli_help_and_version_smoke() -> None:
    help_result = runner.invoke(app, ["--help"])
    version_result = runner.invoke(app, ["version"])
    assert help_result.exit_code == 0
    assert version_result.exit_code == 0
    assert __version__ in version_result.stdout


def test_release_command_set_smoke() -> None:
    diff_result = runner.invoke(
        app,
        [
            "diff",
            "tests/fixtures/diff/base_artifact.json",
            "tests/fixtures/diff/changed_artifact.json",
        ],
    )
    lint_result = runner.invoke(app, ["lint", "tests/fixtures/lint/weak_artifact.json"])
    assert diff_result.exit_code == 0
    assert lint_result.exit_code == 0
