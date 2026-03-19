from __future__ import annotations

from pathlib import Path
from typing import cast

import typer

from sr8.compiler import CompileConfig, compile_intent
from sr8.io.exporters import load_artifact
from sr8.io.writers import write_artifact
from sr8.models.intent_artifact import IntentArtifact
from sr8.models.source_intent import SourceType
from sr8.profiles.registry import apply_profile_overlay
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
def init(target: str = typer.Argument(".", help="Target workspace path.")) -> None:
    """Initialize an SR8 workspace shell."""
    typer.echo(f"Initialized SR8 workspace scaffold at: {target}")


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
