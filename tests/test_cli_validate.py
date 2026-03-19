from pathlib import Path

from typer.testing import CliRunner

from sr8.cli import app
from sr8.compiler import CompileConfig, compile_intent
from sr8.io.writers import write_artifact

runner = CliRunner()


def test_cli_validate_reports_status(tmp_path: Path) -> None:
    result = compile_intent(
        source="tests/fixtures/founder_generic.md",
        config=CompileConfig(profile="generic"),
    )
    artifact_path, _ = write_artifact(result.artifact, out_dir=tmp_path, export_format="json")

    output = runner.invoke(app, ["validate", str(artifact_path)])
    assert output.exit_code == 0
    assert "Validation:" in output.stdout
    assert "errors=0" in output.stdout
