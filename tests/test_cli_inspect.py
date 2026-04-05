from pathlib import Path

from typer.testing import CliRunner

from sr8.cli import app
from sr8.compiler import CompileConfig, compile_intent
from sr8.io.writers import write_artifact

runner = CliRunner()


def test_cli_inspect_artifact_path(tmp_path: Path) -> None:
    result = compile_intent(
        source="tests/fixtures/repo_audit_request.md",
        config=CompileConfig(profile="repo_audit"),
    )
    artifact_path, _ = write_artifact(result.artifact, out_dir=tmp_path, export_format="json")
    output = runner.invoke(app, ["inspect", str(artifact_path)])
    assert output.exit_code == 0
    assert "Artifact ID:" in output.stdout
    assert "Profile:" in output.stdout
    assert "Source Hash:" in output.stdout
    assert "Extraction Trust:" in output.stdout
