from pathlib import Path


def test_compile_route_surfaces_async_and_trust_panels() -> None:
    compile_page = Path("frontend/src/routes/compile/+page.svelte").read_text(encoding="utf-8")

    assert "TrustPanel" in compile_page
    assert 'name="async_mode"' in compile_page
    assert 'name="idempotency_key"' in compile_page


def test_artifact_detail_route_validates_loaded_canonical_artifacts() -> None:
    artifact_server = Path("frontend/src/routes/artifacts/[id]/+page.server.ts").read_text(
        encoding="utf-8"
    )
    artifact_page = Path("frontend/src/lib/components/artifacts/ArtifactDetail.svelte").read_text(
        encoding="utf-8"
    )

    assert "client.validate({ artifact_path: record.file_path })" in artifact_server
    assert "ValidationSummaryPanel" in artifact_page


def test_transform_lint_diff_pages_unwrap_report_payloads() -> None:
    transform_page = Path("frontend/src/routes/transforms/+page.svelte").read_text(
        encoding="utf-8"
    )
    lint_page = Path("frontend/src/routes/lint/+page.svelte").read_text(encoding="utf-8")
    diff_page = Path("frontend/src/routes/diff/+page.svelte").read_text(encoding="utf-8")

    assert "form?.result?.payload?.content" in transform_page
    assert "form?.result?.payload" in lint_page
    assert "form?.result?.payload" in diff_page
