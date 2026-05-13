from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from sr8.api.app import app as api_app
from sr8.cli import app


def test_schema_export_and_validate(tmp_path: Path) -> None:
    runner = CliRunner()
    schema_path = tmp_path / "intent_artifact.schema.json"
    export = runner.invoke(app, ["schema", "export", "--out", str(schema_path)])

    assert export.exit_code == 0
    assert schema_path.exists()
    assert "IntentArtifact" in schema_path.read_text(encoding="utf-8")


def test_proof_run_creates_required_tree(tmp_path: Path) -> None:
    runner = CliRunner()
    proof_dir = tmp_path / "proof"
    result = runner.invoke(
        app,
        [
            "proof",
            "run",
            "examples/product_prd.md",
            "--profile",
            "prd",
            "--mode",
            "rules",
            "--out",
            str(proof_dir),
        ],
    )

    assert result.exit_code == 0, result.stdout
    for rel in (
        "input/product_prd.md",
        "canonical/artifact.json",
        "derivative_markdown/artifact.md",
        "derivative_srxml/artifact.xml",
        "receipts/compile_receipt.json",
        "validation/validation_report.json",
        "lint/lint_report.json",
        "diff/diff_report.json",
        "hashes.json",
        "command_transcript.log",
        "proof_manifest.json",
    ):
        assert (proof_dir / rel).exists()


def test_api_compile_persist_false_and_true(tmp_path: Path, monkeypatch) -> None:
    workspace = tmp_path / ".sr8"
    monkeypatch.setenv("SR8_WORKSPACE_PATH", str(workspace))
    client = TestClient(api_app)

    payload = {
        "source": "Objective: API persistence\nScope:\n- one\n",
        "profile": "generic",
        "mode": "rules",
    }
    stateless = client.post("/compile", json=payload)
    assert stateless.status_code == 200
    assert stateless.json()["persistence"]["persisted"] is False
    assert not (workspace / "artifacts" / "canonical").exists()

    persisted = client.post("/compile", json={**payload, "persist": True})
    assert persisted.status_code == 200
    assert persisted.json()["persistence"]["persisted"] is True
    assert Path(persisted.json()["persistence"]["artifact_path"]).exists()
    assert Path(persisted.json()["persistence"]["receipt_path"]).exists()
