from sr8.models.intent_artifact import ArtifactSource, GovernanceFlags, IntentArtifact
from sr8.models.lineage import Lineage
from sr8.models.receipts import CompilationReceipt
from sr8.models.source_intent import SourceIntent
from sr8.models.validation import ValidationIssue, ValidationReport


def test_models_instantiate() -> None:
    source_intent = SourceIntent(
        source_id="src-001",
        source_type="text",
        raw_content="compile this",
        normalized_content="compile this",
        source_hash="abc123",
    )

    lineage = Lineage(
        compile_run_id="run-001",
        pipeline_version="0.1.0",
        source_hash=source_intent.source_hash,
    )

    report = ValidationReport(
        report_id="report-001",
        readiness_status="warn",
        summary="warning",
    )

    artifact = IntentArtifact(
        artifact_id="artifact-001",
        artifact_version="1.0.0",
        compiler_version="0.1.0",
        created_at=source_intent.ingested_at,
        source=ArtifactSource(
            source_id=source_intent.source_id,
            source_type=source_intent.source_type,
            source_hash=source_intent.source_hash,
        ),
        objective="compile this",
        lineage=lineage,
        validation=report,
        governance_flags=GovernanceFlags(requires_human_review=True),
    )

    receipt = CompilationReceipt(
        receipt_id="receipt-001",
        artifact_id=artifact.artifact_id,
        source_hash=source_intent.source_hash,
        status="accepted",
        notes=["ok"],
    )

    issue = ValidationIssue(code="E001", message="example", severity="warning")
    assert source_intent.source_id == "src-001"
    assert artifact.source.source_hash == source_intent.source_hash
    assert lineage.pipeline_version == "0.1.0"
    assert report.readiness_status == "warn"
    assert receipt.status == "accepted"
    assert issue.severity == "warning"
