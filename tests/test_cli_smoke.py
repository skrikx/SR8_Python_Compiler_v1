from typer.testing import CliRunner

from sr8.cli import app
from sr8.version import __version__

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "SR8 CLI" in result.stdout


def test_cli_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_cli_init_default() -> None:
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Initialized SR8 workspace at:" in result.stdout


def test_cli_inspect_default() -> None:
    result = runner.invoke(app, ["inspect", "tests/fixtures/ambiguous_request.txt"])
    assert result.exit_code == 0
    assert "Artifact ID:" in result.stdout
