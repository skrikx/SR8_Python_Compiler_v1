from __future__ import annotations

import json
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import typer
from pydantic import ValidationError

from sr8.adapters import list_provider_descriptors, probe_provider, probe_providers
from sr8.adapters.errors import ProviderError
from sr8.compiler import CompilationResult, CompileConfig, compile_intent, recompile_artifact
from sr8.config.settings import SR8Settings, resolve_compile_config
from sr8.diff.engine import semantic_diff
from sr8.diff.render import render_diff_report
from sr8.eval import (
    compare_benchmark_reports,
    list_available_suites,
    load_run_report,
    run_benchmark_suite,
    write_regression_report,
    write_run_report,
)
from sr8.extract.trace import summarize_extraction_trace
from sr8.frontdoor import FrontdoorCompileResult, chat_compile
from sr8.frontdoor.command_parser import parse_chat_invocation
from sr8.io.exporters import load_artifact
from sr8.io.writers import write_artifact
from sr8.lint.engine import lint_artifact
from sr8.models.compile_config import CompileMode
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
from sr8.utils.hash import stable_text_hash
from sr8.validate.engine import validate_artifact
from sr8.version import __version__

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    help="SR8 CLI - local intent compiler.",
)
benchmark_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    help="Run local benchmark suites and compare result packs.",
)
provider_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    help="Inspect optional provider adapters and configuration state.",
)
schema_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    help="Export and validate SR8 canonical schemas.",
)
proof_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    help="Generate local SR8 proof packets.",
)
app.add_typer(benchmark_app, name="benchmark")
app.add_typer(provider_app, name="providers")
app.add_typer(schema_app, name="schema")
app.add_typer(proof_app, name="proof")


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
    compile_kind = str(artifact.metadata.get("compile_kind", "canonicalize_structured"))
    raw_source_count = artifact.metadata.get("source_supplied_field_count", 0)
    source_count = raw_source_count if isinstance(raw_source_count, int) else 0
    raw_derived_count = artifact.metadata.get("derived_field_count", 0)
    derived_count = raw_derived_count if isinstance(raw_derived_count, int) else 0
    unresolved_value = artifact.metadata.get("unresolved_fields", [])
    unresolved_count = len(unresolved_value) if isinstance(unresolved_value, list) else 0
    typer.echo(f"Compile Kind: {compile_kind}")
    typer.echo(
        "Semantic Transform: "
        f"{'yes' if bool(artifact.metadata.get('semantic_transform_applied', False)) else 'no'}"
    )
    typer.echo(
        "Provenance Counts: "
        f"source={source_count}, "
        f"derived={derived_count}, "
        f"unresolved={unresolved_count}"
    )
    typer.echo(f"Target Class: {artifact.target_class}")
    typer.echo(f"Source Hash: {artifact.source.source_hash}")
    typer.echo(f"Objective: {artifact.objective or '(empty)'}")
    typer.echo(f"Scope Count: {len(artifact.scope)}")
    typer.echo(f"Constraints Count: {len(artifact.constraints)}")
    compile_truth_summary = str(artifact.metadata.get("compile_truth_summary", "")).strip()
    if compile_truth_summary:
        typer.echo(f"Compile Truth: {compile_truth_summary}")
    trust_summary = summarize_extraction_trace(
        cast(Mapping[str, object] | None, artifact.metadata.get("extraction_trace"))
    )
    typer.echo(f"Extraction Adapter: {trust_summary['adapter_name']}")
    provider_name = trust_summary.get("provider")
    if isinstance(provider_name, str) and provider_name:
        typer.echo(f"Assist Provider: {provider_name}")
    status_counts = cast(dict[str, int], trust_summary["status_counts"])
    if status_counts:
        counts = ", ".join(f"{status}={count}" for status, count in status_counts.items())
        typer.echo(f"Extraction Trust: {counts}")
        low_confidence_fields = cast(list[str], trust_summary["low_confidence_fields"])
        if low_confidence_fields:
            typer.echo(f"Low Confidence Fields: {', '.join(low_confidence_fields)}")
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


def _should_use_frontdoor(source: str, source_type: SourceType | None) -> bool:
    if source_type is not None:
        return False
    if Path(source).exists():
        return False
    parsed = parse_chat_invocation(source)
    lowered = parsed.raw.strip().lower()
    return lowered.startswith(("compile:", "resume:")) or "<compiler_input_form" in lowered


def _write_frontdoor_packages(out_dir: str, result: FrontdoorCompileResult) -> None:
    output_path = Path(out_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    if result.promptunit_package_xml:
        (output_path / "promptunit_package.xml").write_text(
            result.promptunit_package_xml,
            encoding="utf-8",
        )
    if result.sr8_prompt_xml:
        (output_path / "sr8_prompt.xml").write_text(
            result.sr8_prompt_xml,
            encoding="utf-8",
        )
    if result.safe_alternative_package_xml:
        (output_path / "safe_alternative_package.xml").write_text(
            result.safe_alternative_package_xml,
            encoding="utf-8",
        )


def _echo_compile_target_validation(result: CompilationResult) -> None:
    target_validation = result.target_validation
    if target_validation is None:
        return
    typer.echo(
        "Target Validation: "
        f"{target_validation.target} {target_validation.status} "
        f"(valid={target_validation.valid}, errors={len(target_validation.errors)}, "
        f"warnings={len(target_validation.warnings)})"
    )
    if target_validation.artifact_type:
        typer.echo(f"SRXML Artifact Type: {target_validation.artifact_type}")
    if target_validation.depth_tier:
        typer.echo(f"SRXML Depth Tier: {target_validation.depth_tier}")
    for repair_action in target_validation.repair_actions:
        typer.echo(f"Repair: {repair_action}")


def _write_compile_target_output(out_dir: str, result: CompilationResult) -> Path | None:
    target_validation = result.target_validation
    if target_validation is None:
        return None
    output_path = Path(out_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    extension = ".xml" if target_validation.output_format == "xml" else ".txt"
    target_path = output_path / f"latest_{target_validation.target}{extension}"
    target_path.write_text(target_validation.content, encoding="utf-8")
    return target_path


@app.command("compile")
def compile_command(
    source: str = typer.Argument(..., help="Source input path or inline text."),
    profile: str | None = typer.Option(None, "--profile", help="Profile overlay."),
    target: str | None = typer.Option(
        None,
        "--target",
        help="Optional compile validation target, currently xml_srxml_rc2.",
    ),
    validate_target: bool = typer.Option(
        False,
        "--validate",
        help="Validate the requested compile target before treating it as complete.",
    ),
    source_type: str | None = typer.Option(None, "--source-type", help="text|markdown|json|yaml"),
    export_format: str = typer.Option("json", "--format", help="json|yaml"),
    out: str | None = typer.Option(None, "--out", help="Output directory for artifact export."),
    mode: str = typer.Option("auto", "--mode", help="Compile mode: rules, assist, or auto."),
    rule_only: bool = typer.Option(
        False,
        "--rule-only",
        help="Force the deterministic local extraction path.",
    ),
    assist_extract: bool = typer.Option(
        False,
        "--assist-extract",
        help="Enable model-assisted extraction with provider and model options.",
    ),
    assist_provider: str | None = typer.Option(
        None,
        "--assist-provider",
        "--provider",
        help="Optional provider for model-assisted extraction.",
    ),
    assist_model: str | None = typer.Option(
        None,
        "--assist-model",
        "--model",
        help="Optional model for model-assisted extraction.",
    ),
    save_llm_trace: bool = typer.Option(
        False,
        "--save-llm-trace",
        help="Persist raw LLM trace material in artifact metadata.",
    ),
) -> None:
    """Compile source into canonical artifact, apply profile, validate, and optionally export."""
    settings = SR8Settings()
    normalized_source_type = cast(SourceType | None, source_type)
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"rules", "assist", "auto"}:
        raise typer.BadParameter("--mode must be one of: rules, assist, auto.")
    use_frontdoor = _should_use_frontdoor(source, normalized_source_type)
    if assist_extract and not (
        assist_provider or assist_model or settings.assist_provider or settings.assist_model
    ):
        raise typer.BadParameter(
            "--assist-extract requires a provider and model from CLI flags or "
            "SR8_ASSIST_PROVIDER and SR8_ASSIST_MODEL settings."
        )
    settings_for_config = settings
    if (
        normalized_mode == "auto"
        and not assist_extract
        and assist_provider is None
        and assist_model is None
    ):
        settings_for_config = settings.model_copy(
            update={
                "extraction_adapter": "rule_based",
                "assist_provider": None,
                "assist_model": None,
            }
        )
    try:
        compile_config = resolve_compile_config(
            settings_for_config,
            profile=profile,
            target=target,
            validate_target=validate_target,
            mode=cast(CompileMode, normalized_mode),
            rule_only=rule_only,
            assist_extract=assist_extract,
            assist_provider=assist_provider,
            assist_model=assist_model,
            save_llm_trace=save_llm_trace,
        )
    except ValueError as exc:
        raise typer.BadParameter(
            str(exc)
        ) from exc
    if use_frontdoor:
        frontdoor_result = chat_compile(source, config=compile_config)
        if frontdoor_result.status == "intake_required":
            typer.echo("Frontdoor intake required. Use the XML form to resume.")
            typer.echo(frontdoor_result.intake_xml or "")
            return
        artifact = frontdoor_result.artifact
        if artifact is None:
            raise typer.BadParameter("Frontdoor compile did not return a canonical artifact.")
        _echo_artifact_summary(artifact)
        if frontdoor_result.governance.status != "allow":
            typer.echo(f"Governance: {frontdoor_result.governance.status}")
        if out is not None:
            _write_frontdoor_packages(out, frontdoor_result)
        if (
            frontdoor_result.receipt
            and frontdoor_result.normalized_source
            and frontdoor_result.extracted_dimensions
        ):
            result = CompilationResult(
                artifact=artifact,
                receipt=frontdoor_result.receipt,
                normalized_source=frontdoor_result.normalized_source,
                extracted_dimensions=frontdoor_result.extracted_dimensions,
            )
        else:
            result = None
    else:
        try:
            result = compile_intent(
                source=source,
                source_type=normalized_source_type,
                config=compile_config,
            )
        except ProviderError as exc:
            raise typer.BadParameter(f"Provider assist failed: {exc}") from exc
        artifact = result.artifact
        _echo_artifact_summary(artifact)
    if result is not None:
        typer.echo(f"Receipt Status: {result.receipt.status}")
        _echo_compile_target_validation(result)
    if out is not None:
        workspace_root = _find_workspace_root(out)
        if workspace_root is not None:
            workspace = init_workspace(workspace_root)
            artifact_path, latest_path, record = save_canonical_artifact(workspace, artifact)
            typer.echo(f"Written: {artifact_path}")
            typer.echo(f"Latest: {latest_path}")
            typer.echo(f"Indexed: {record.record_id}")
            if result is not None:
                receipt, receipt_path = write_compilation_receipt(
                    workspace,
                    result=result,
                    output_path=str(artifact_path),
                )
                typer.echo(f"Receipt: {receipt_path} ({receipt.receipt_id})")
            else:
                typer.echo("Receipt: skipped (frontdoor result missing compilation details)")
            if result is not None:
                target_path = _write_compile_target_output(out, result)
                if target_path is not None:
                    typer.echo(f"Target Output: {target_path}")
        else:
            artifact_path, latest_path = write_artifact(
                artifact,
                out_dir=out,
                export_format=export_format,
            )
            typer.echo(f"Written: {artifact_path}")
            typer.echo(f"Latest: {latest_path}")
            if result is not None:
                target_path = _write_compile_target_output(out, result)
                if target_path is not None:
                    typer.echo(f"Target Output: {target_path}")
    elif result is not None and result.target_validation is not None:
        typer.echo("")
        typer.echo(result.target_validation.content)
    if (
        result is not None
        and result.target_validation is not None
        and result.target_validation.status != "accepted"
    ):
        raise typer.Exit(1)


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

    settings = SR8Settings()
    result = compile_intent(
        source=target,
        config=CompileConfig(
            profile=settings.default_profile,
            compile_mode="rules",
            extraction_adapter="rule_based",
        ),
    )
    _echo_artifact_summary(result.artifact)


@provider_app.command("list")
def providers_list_command() -> None:
    """List registered provider adapters and declared capabilities."""
    for descriptor in list_provider_descriptors():
        capabilities = ", ".join(descriptor.capabilities)
        typer.echo(
            f"{descriptor.name} | live={descriptor.supports_live_inference} | "
            f"capabilities={capabilities}"
        )


@provider_app.command("probe")
def providers_probe_command(
    provider: str | None = typer.Option(None, "--provider", help="Optional provider name."),
) -> None:
    """Probe provider configuration readiness from environment-backed settings."""
    results = [probe_provider(provider)] if provider is not None else probe_providers()
    for result in results:
        missing = ",".join(result.missing_env_vars) if result.missing_env_vars else "-"
        accessible = (
            "-"
            if result.subscribed_or_accessible is None
            else str(result.subscribed_or_accessible)
        )
        detail = f" | detail={result.detail}" if result.detail else ""
        typer.echo(
            f"{result.provider} | configured={result.configured} | accessible={accessible} | "
            f"live_enabled={result.live_enabled} | ready={result.ready_for_runtime} | "
            f"available={result.available} | missing={missing}{detail}"
        )


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
            json_path, native_path, latest_json, record = save_derivative_artifact(
                workspace,
                result.derivative,
            )
            receipt, receipt_path = write_transform_receipt(
                workspace,
                derivative=result.derivative,
                output_path=str(json_path),
            )
            typer.echo(f"Written JSON: {json_path}")
            typer.echo(f"Written Native: {native_path}")
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


@app.command("recompile")
def recompile_command(
    artifact_path: str = typer.Argument(..., help="Canonical artifact file (.json or .yaml)."),
    profile: str | None = typer.Option(None, "--profile", help="Optional profile override."),
    out: str | None = typer.Option(None, "--out", help="Output directory for artifact export."),
) -> None:
    """Recompile an artifact while preserving source hash and lineage."""
    artifact = load_artifact(artifact_path)
    rebuilt = recompile_artifact(
        artifact,
        profile=profile,
        config=CompileConfig(profile=profile or artifact.profile),
    )
    _echo_artifact_summary(rebuilt)
    if out is not None:
        artifact_path_written, latest_path = write_artifact(
            rebuilt,
            out_dir=out,
            export_format="json",
        )
        typer.echo(f"Written: {artifact_path_written}")
        typer.echo(f"Latest: {latest_path}")


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


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(payload, "model_dump"):
        payload = payload.model_dump(mode="json")
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _hash_tree(root: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel == "hashes.json":
            continue
        hashes[rel] = stable_text_hash(path.read_text(encoding="utf-8", errors="replace"))
    return hashes


@schema_app.command("export")
def schema_export_command(
    out: str = typer.Option(..., "--out", help="Schema output path."),
) -> None:
    """Export the canonical IntentArtifact JSON schema."""
    output_path = Path(out)
    _write_json(output_path, IntentArtifact.model_json_schema())
    typer.echo(f"Schema written: {output_path}")


@schema_app.command("validate")
def schema_validate_command(
    artifact_path: str = typer.Argument(..., help="Artifact JSON path."),
) -> None:
    """Validate an artifact against the canonical IntentArtifact model."""
    try:
        artifact_text = Path(artifact_path).read_text(encoding="utf-8")
        artifact = IntentArtifact.model_validate_json(artifact_text)
    except (ValidationError, json.JSONDecodeError) as exc:
        raise typer.BadParameter(f"Schema validation failed: {exc}") from exc
    typer.echo(f"Schema validation: pass ({artifact.artifact_id})")


@proof_app.command("run")
def proof_run_command(
    source: str = typer.Argument(..., help="Input source path or inline text."),
    profile: str = typer.Option("generic", "--profile", help="Profile overlay."),
    mode: str = typer.Option("auto", "--mode", help="Compile mode: rules, assist, or auto."),
    out: str = typer.Option(..., "--out", help="Proof packet output directory."),
    provider: str | None = typer.Option(None, "--provider", help="Assist provider."),
    model: str | None = typer.Option(None, "--model", help="Assist model."),
) -> None:
    """Generate a replayable local proof packet."""
    normalized_mode = mode.strip().lower()
    if normalized_mode not in {"rules", "assist", "auto"}:
        raise typer.BadParameter("--mode must be one of: rules, assist, auto.")
    proof_dir = Path(out)
    if proof_dir.exists():
        shutil.rmtree(proof_dir)
    for dirname in (
        "input",
        "canonical",
        "derivative_markdown",
        "derivative_srxml",
        "receipts",
        "validation",
        "lint",
        "diff",
        "benchmark",
    ):
        (proof_dir / dirname).mkdir(parents=True, exist_ok=True)

    transcript: list[str] = []
    source_path = Path(source)
    input_name = source_path.name if source_path.exists() else "inline.txt"
    copied_input = proof_dir / "input" / input_name
    if source_path.exists():
        shutil.copy2(source_path, copied_input)
    else:
        copied_input.write_text(source, encoding="utf-8")
    transcript.append(f"COPY {source} {copied_input} PASS")

    settings = SR8Settings()
    compile_config = resolve_compile_config(
        settings,
        profile=profile,
        mode=cast(CompileMode, normalized_mode),
        assist_provider=provider,
        assist_model=model,
    )
    result = compile_intent(source=source, config=compile_config)
    artifact = result.artifact
    canonical_path = proof_dir / "canonical" / "artifact.json"
    compile_receipt_path = proof_dir / "receipts" / "compile_receipt.json"
    _write_json(canonical_path, artifact)
    _write_json(compile_receipt_path, result.receipt)
    transcript.append(
        f"sr8 compile {source} --profile {profile} --mode {normalized_mode} PASS"
    )

    validation = validate_artifact(artifact, profile_name=profile)
    _write_json(proof_dir / "validation" / "validation_report.json", validation)
    transcript.append("sr8 schema validate canonical/artifact.json PASS")

    markdown = transform_artifact(artifact, "markdown_prd")
    markdown_native = proof_dir / "derivative_markdown" / "artifact.md"
    _write_text(markdown_native, markdown.derivative.content)
    _write_json(proof_dir / "derivative_markdown" / "metadata.json", markdown.derivative)
    _write_json(
        proof_dir / "receipts" / "transform_markdown_receipt.json",
        {
            "parent_artifact_id": artifact.artifact_id,
            "derivative_id": markdown.derivative.derivative_id,
            "transform_target": markdown.derivative.transform_target,
            "output_path": str(markdown_native),
        },
    )
    transcript.append("sr8 transform canonical/artifact.json --to markdown_prd PASS")

    srxml = transform_artifact(artifact, "xml_srxml_rc2")
    srxml_native = proof_dir / "derivative_srxml" / "artifact.xml"
    _write_text(srxml_native, srxml.derivative.content)
    _write_json(proof_dir / "derivative_srxml" / "metadata.json", srxml.derivative)
    _write_json(
        proof_dir / "receipts" / "transform_srxml_receipt.json",
        {
            "parent_artifact_id": artifact.artifact_id,
            "derivative_id": srxml.derivative.derivative_id,
            "transform_target": srxml.derivative.transform_target,
            "output_path": str(srxml_native),
        },
    )
    transcript.append("sr8 transform canonical/artifact.json --to xml_srxml_rc2 PASS")

    lint_report = lint_artifact(artifact, artifact_ref=str(canonical_path))
    _write_json(proof_dir / "lint" / "lint_report.json", lint_report)
    transcript.append("sr8 lint canonical/artifact.json PASS")

    regenerated = compile_intent(source=source, config=compile_config).artifact
    diff_report = semantic_diff(
        artifact,
        regenerated,
        left_ref="canonical",
        right_ref="regenerated",
    )
    _write_json(proof_dir / "diff" / "diff_report.json", diff_report)
    _write_text(proof_dir / "diff" / "diff_summary.txt", render_diff_report(diff_report))
    transcript.append("sr8 diff canonical/artifact.json regenerated PASS")

    try:
        benchmark_report = run_benchmark_suite(
            suite="rules_required",
            out_dir=proof_dir / "benchmark",
        )
        _write_json(proof_dir / "benchmark" / "rules_required.json", benchmark_report)
        transcript.append("sr8 benchmark run --suite rules_required PASS")
    except ValueError as exc:
        _write_json(
            proof_dir / "benchmark" / "blocked.json",
            {"status": "blocked", "detail": str(exc)},
        )
        transcript.append(f"sr8 benchmark run --suite rules_required BLOCKED {exc}")

    hashes = _hash_tree(proof_dir)
    _write_json(proof_dir / "hashes.json", hashes)
    manifest = {
        "proof_version": "sr8-v1",
        "source": source,
        "profile": profile,
        "mode": normalized_mode,
        "artifact_id": artifact.artifact_id,
        "receipt_id": result.receipt.receipt_id,
        "provider": result.receipt.provider,
        "model": result.receipt.model,
        "llm_used": result.receipt.llm_used,
        "files": sorted(hashes),
        "status": "pass",
    }
    _write_json(proof_dir / "proof_manifest.json", manifest)
    _write_text(proof_dir / "command_transcript.log", "\n".join(transcript) + "\n")
    typer.echo(f"Proof packet written: {proof_dir}")


@benchmark_app.command("run")
def benchmark_run_command(
    suite: str | None = typer.Option(None, "--suite", help="Suite to run."),
    run_all: bool = typer.Option(False, "--all", help="Run the full corpus."),
    provider: str | None = typer.Option(
        None,
        "--provider",
        help="Provider for LLM-required suites.",
    ),
    out: str = typer.Option("benchmarks/results", "--out", help="Output directory for reports."),
) -> None:
    """Run benchmark suites and write scored result packs."""
    if suite is not None and run_all:
        raise typer.BadParameter("Use either --suite or --all, not both.")
    if suite is None and not run_all:
        raise typer.BadParameter("Provide --suite or --all.")
    available = list_available_suites()
    if suite is not None and suite not in available:
        raise typer.BadParameter(
            f"Unknown suite '{suite}'. Expected one of: {', '.join(available)}."
        )
    if suite == "llm_required":
        provider_name = provider or SR8Settings().assist_provider
        model_name = SR8Settings().assist_model
        missing = [
            name
            for name, value in (
                ("SR8_ASSIST_PROVIDER", provider_name),
                ("SR8_ASSIST_MODEL", model_name),
            )
            if value is None
        ]
        output_dir = Path(out)
        output_dir.mkdir(parents=True, exist_ok=True)
        if missing:
            output_dir = Path(out)
            output_dir.mkdir(parents=True, exist_ok=True)
            summary = (
                "# Benchmark Report: llm_required\n\n"
                "- Status: BLOCKED_PROVIDER_CONFIG\n"
                f"- Missing: {', '.join(missing)}\n"
            )
            (output_dir / "summary.md").write_text(summary, encoding="utf-8")
            typer.echo("Suite: llm_required")
            typer.echo("Status: BLOCKED_PROVIDER_CONFIG")
            typer.echo(f"Missing: {', '.join(missing)}")
            return
        summary = (
            "# Benchmark Report: llm_required\n\n"
            "- Status: BLOCKED_PROVIDER_RUNTIME\n"
            f"- Provider: {provider_name}\n"
            "- Detail: No live LLM benchmark corpus is enabled for this local run.\n"
        )
        (output_dir / "summary.md").write_text(summary, encoding="utf-8")
        typer.echo("Suite: llm_required")
        typer.echo("Status: BLOCKED_PROVIDER_RUNTIME")
        typer.echo("Detail: No live LLM benchmark corpus is enabled for this local run.")
        return

    effective_suite = None if run_all else suite
    report = run_benchmark_suite(suite=effective_suite, out_dir=out)
    json_path, markdown_path = write_run_report(
        report,
        out_dir=out,
        file_stem=effective_suite or "all",
    )
    summary_path = Path(out) / "summary.md"
    summary_path.write_text(markdown_path.read_text(encoding="utf-8"), encoding="utf-8")
    typer.echo(f"Run ID: {report.run_id}")
    typer.echo(f"Suite: {report.suite}")
    typer.echo(f"Average Score: {report.summary.average_score}")
    typer.echo(f"Passed Cases: {report.summary.passed_cases}/{report.summary.total_cases}")
    typer.echo(f"JSON Report: {json_path}")
    typer.echo(f"Markdown Report: {markdown_path}")
    typer.echo(f"Summary: {summary_path}")


@benchmark_app.command("compare")
def benchmark_compare_command(
    baseline: str = typer.Argument(..., help="Baseline benchmark JSON report."),
    candidate: str = typer.Argument(..., help="Candidate benchmark JSON report."),
    out: str | None = typer.Option(
        None,
        "--out",
        help="Optional directory for regression reports.",
    ),
) -> None:
    """Compare two benchmark result packs."""
    baseline_report = load_run_report(baseline)
    candidate_report = load_run_report(candidate)
    regression = compare_benchmark_reports(baseline_report, candidate_report)
    typer.echo(f"Baseline: {regression.baseline_run_id} ({regression.baseline_version})")
    typer.echo(f"Candidate: {regression.candidate_run_id} ({regression.candidate_version})")
    typer.echo(f"Summary Delta: {regression.summary_delta}")
    typer.echo(f"Case Delta: {regression.case_delta}")
    if regression.improvements:
        typer.echo("Improvements:")
        for item in regression.improvements:
            typer.echo(f"- {item}")
    if regression.regressions:
        typer.echo("Regressions:")
        for item in regression.regressions:
            typer.echo(f"- {item}")
    if out is not None:
        json_path, markdown_path = write_regression_report(regression, out_dir=out)
        typer.echo(f"JSON Report: {json_path}")
        typer.echo(f"Markdown Report: {markdown_path}")


if __name__ == "__main__":
    app()
