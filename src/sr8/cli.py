from __future__ import annotations

from pathlib import Path
from typing import cast

import typer

from sr8.compiler import CompileConfig, compile_intent
from sr8.diff.engine import semantic_diff
from sr8.diff.render import render_diff_report
from sr8.io.exporters import load_artifact
from sr8.io.writers import write_artifact
from sr8.lint.engine import lint_artifact
from sr8.models.derivative_artifact import DerivativeArtifact
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.source_intent import SourceType
from sr8.profiles.registry import apply_profile_overlay
from sr8.storage.catalog import list_catalog, show_catalog_record
from sr8.storage.load import load_by_id
from sr8.storage.receipts import write_compilation_receipt, write_transform_receipt
from sr8.storage.save import save_canonical_artifact, save_derivative_artifact
from sr8.storage.workspace import init_workspace
from sr8.transform.engine import transform_artifact, write_derivative
from sr8.validate.engine import validate_artifact
from sr8.version import __version__

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="SR8 CLI - local intent compiler.",
)


@app.command("version")
def version() -> None:
    """Print the SR8 package version."""
    typer.echo(__version__)


@app.command("init")
def init(path: str = typer.Option(".sr8", "--path", help="Workspace root path.")) -> None:
    """Initialize a local SR8 workspace."""
    workspace = init_workspace(path)
    typer.echo(f"Initialized SR8 workspace at: {workspace.root}")


def _echo_validation(artifact: IntentArtifact) -> None:
    report = artifact.validation
    typer.echo(
        f"Validation: {report.readiness_status} "
        f"(errors={len(report.errors)}, warnings={len(report.warnings)})"
    )
    typer.echo(f"Summary: {report.summary}")


def _echo_artifact_summary(artifact: IntentArtifact) -> None:
    typer.echo(f"Artifact ID: {artifact.artifact_id}")
    typer.echo(f"Profile: {artifact.profile}")
    typer.echo(f"Target Class: {artifact.target_class}")
    typer.echo(f"Objective: {artifact.objective or '(empty)'}")
    typer.echo(f"Scope Count: {len(artifact.scope)}")
    typer.echo(f"Constraints Count: {len(artifact.constraints)}")
    _echo_validation(artifact)


def _find_workspace_root(candidate_path: str | Path) -> Path | None:
    candidate = Path(candidate_path).resolve()
    for path in (candidate, *candidate.parents):
        if path.name == ".sr8":
            return path
    return None


def _resolve_canonical_artifact(value: str, workspace_path: str) -> tuple[IntentArtifact, str]:
    candidate = Path(value)
    if candidate.exists():
        return load_artifact(candidate), str(candidate)

    workspace = init_workspace(workspace_path)
    loaded = load_by_id(workspace, value)
    if isinstance(loaded, DerivativeArtifact):
        msg = f"Identifier '{value}' resolves to a derivative artifact, not canonical."
        raise ValueError(msg)
    return loaded, value


@app.command("compile")
def compile_command(
    source: str = typer.Argument(..., help="Source input path or inline text."),
    profile: str = typer.Option("generic", "--profile", help="Profile overlay."),
    source_type: str | None = typer.Option(None, "--source-type", help="text|markdown|json|yaml"),
    export_format: str = typer.Option("json", "--format", help="json|yaml"),
    out: str | None = typer.Option(None, "--out", help="Output directory for artifact export."),
) -> None:
    """Compile source into canonical artifact, apply profile, validate, and optionally export."""
    normalized_source_type = cast(SourceType | None, source_type)
    result = compile_intent(
        source=source,
        source_type=normalized_source_type,
        config=CompileConfig(profile=profile),
    )
    artifact = result.artifact
    _echo_artifact_summary(artifact)
    if out is not None:
        workspace_root = _find_workspace_root(out)
        if workspace_root is not None:
            workspace = init_workspace(workspace_root)
            artifact_path, latest_path, record = save_canonical_artifact(workspace, artifact)
            receipt, receipt_path = write_compilation_receipt(
                workspace,
                result=result,
                output_path=str(artifact_path),
            )
            typer.echo(f"Written: {artifact_path}")
            typer.echo(f"Latest: {latest_path}")
            typer.echo(f"Indexed: {record.record_id}")
            typer.echo(f"Receipt: {receipt_path} ({receipt.receipt_id})")
        else:
            artifact_path, latest_path = write_artifact(
                artifact,
                out_dir=out,
                export_format=export_format,
            )
            typer.echo(f"Written: {artifact_path}")
            typer.echo(f"Latest: {latest_path}")


@app.command("validate")
def validate_command(
    artifact_path: str = typer.Argument(..., help="Artifact file (.json or .yaml)."),
    profile: str | None = typer.Option(None, "--profile", help="Optional profile override."),
) -> None:
    """Validate an existing artifact and print structured report."""
    artifact = load_artifact(artifact_path)
    effective_profile = profile or artifact.profile
    if profile is not None:
        artifact = apply_profile_overlay(artifact, profile)
    report = validate_artifact(artifact, profile_name=effective_profile)
    validated = artifact.model_copy(update={"validation": report})
    _echo_artifact_summary(validated)


@app.command("inspect")
def inspect_command(
    target: str = typer.Argument(..., help="Artifact path or source input path."),
) -> None:
    """Inspect artifact summary or compile source and inspect the result."""
    candidate = Path(target)
    if candidate.exists() and candidate.suffix.lower() in {".json", ".yaml", ".yml"}:
        artifact = load_artifact(candidate)
        _echo_artifact_summary(artifact)
        return

    result = compile_intent(source=target, config=CompileConfig(profile="generic"))
    _echo_artifact_summary(result.artifact)


@app.command("transform")
def transform_command(
    artifact_path: str = typer.Argument(..., help="Canonical artifact file (.json or .yaml)."),
    to: str = typer.Option(..., "--to", help="Transform target."),
    out: str | None = typer.Option(None, "--out", help="Output directory for markdown result."),
) -> None:
    """Transform a canonical artifact into a derivative markdown output."""
    artifact = load_artifact(artifact_path)
    result = transform_artifact(artifact, target=to)
    typer.echo(f"Derivative ID: {result.derivative.derivative_id}")
    typer.echo(f"Parent Artifact: {result.derivative.parent_artifact_id}")
    typer.echo(f"Target: {result.derivative.transform_target}")
    if out is not None:
        workspace_root = _find_workspace_root(out)
        if workspace_root is not None:
            workspace = init_workspace(workspace_root)
            json_path, markdown_path, latest_json, record = save_derivative_artifact(
                workspace,
                result.derivative,
            )
            receipt, receipt_path = write_transform_receipt(
                workspace,
                derivative=result.derivative,
                output_path=str(json_path),
            )
            typer.echo(f"Written JSON: {json_path}")
            typer.echo(f"Written Markdown: {markdown_path}")
            typer.echo(f"Latest JSON: {latest_json}")
            typer.echo(f"Indexed: {record.record_id}")
            typer.echo(f"Receipt: {receipt_path} ({receipt.receipt_id})")
        else:
            derivative_path, latest_path = write_derivative(result.derivative, out)
            typer.echo(f"Written: {derivative_path}")
            typer.echo(f"Latest: {latest_path}")
    else:
        typer.echo("")
        typer.echo(result.derivative.content)


@app.command("list")
def list_command(
    kind: str | None = typer.Option(None, "--kind", help="canonical|derivative"),
    profile: str | None = typer.Option(None, "--profile", help="Filter by profile."),
    path: str = typer.Option(".sr8", "--path", help="Workspace root path."),
) -> None:
    """List persisted artifacts from the local index."""
    workspace = init_workspace(path)
    records = list_catalog(workspace, kind=kind, profile=profile)
    if not records:
        typer.echo("No records found.")
        return
    for record in records:
        typer.echo(
            f"{record.record_id} | {record.artifact_kind} | {record.artifact_id} | "
            f"profile={record.profile} | status={record.readiness_status}"
        )


@app.command("show")
def show_command(
    identifier: str = typer.Argument(..., help="Record ID or artifact ID."),
    path: str = typer.Option(".sr8", "--path", help="Workspace root path."),
) -> None:
    """Show indexed record metadata and storage path."""
    workspace = init_workspace(path)
    record = show_catalog_record(workspace, identifier)
    typer.echo(f"Record: {record.record_id}")
    typer.echo(f"Artifact ID: {record.artifact_id}")
    typer.echo(f"Kind: {record.artifact_kind}")
    typer.echo(f"Profile: {record.profile}")
    typer.echo(f"Target Class: {record.target_class}")
    typer.echo(f"Transform Target: {record.transform_target or '-'}")
    typer.echo(f"Parent Artifact: {record.parent_artifact_id or '-'}")
    typer.echo(f"Path: {record.file_path}")


@app.command("diff")
def diff_command(
    left: str = typer.Argument(..., help="Left artifact path or ID."),
    right: str = typer.Argument(..., help="Right artifact path or ID."),
    path: str = typer.Option(".sr8", "--path", help="Workspace root for ID resolution."),
) -> None:
    """Compare two canonical artifacts semantically."""
    left_artifact, left_ref = _resolve_canonical_artifact(left, path)
    right_artifact, right_ref = _resolve_canonical_artifact(right, path)
    report = semantic_diff(left_artifact, right_artifact, left_ref=left_ref, right_ref=right_ref)
    typer.echo(render_diff_report(report))


@app.command("lint")
def lint_command(
    artifact_ref: str = typer.Argument(..., help="Artifact path or ID."),
    path: str = typer.Option(".sr8", "--path", help="Workspace root for ID resolution."),
) -> None:
    """Run artifact quality lint rules."""
    artifact, resolved_ref = _resolve_canonical_artifact(artifact_ref, path)
    report = lint_artifact(artifact, artifact_ref=resolved_ref)
    typer.echo(f"Lint Report: {report.report_id}")
    typer.echo(f"Artifact: {report.artifact_ref}")
    typer.echo(f"Status: {report.status}")
    typer.echo(f"Summary: {report.summary}")
    for finding in report.findings:
        typer.echo(
            f"- {finding.rule_id} [{finding.severity}] {finding.artifact_field}: {finding.message}"
        )
