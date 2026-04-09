from sr8.compiler import CompileConfig, compile_intent, recompile_artifact


def test_recompile_generates_distinct_artifact_and_preserves_parent_lineage() -> None:
    compiled = compile_intent(
        "tests/fixtures/product_prd.md",
        config=CompileConfig(profile="prd"),
    ).artifact

    rebuilt = recompile_artifact(compiled, profile="whitepaper_outline")

    assert rebuilt.artifact_id != compiled.artifact_id
    assert rebuilt.profile == "whitepaper_outline"
    assert rebuilt.source.source_hash == compiled.source.source_hash
    assert rebuilt.lineage.parent_source_hash == compiled.lineage.source_hash
    assert rebuilt.lineage.parent_compile_run_id == compiled.lineage.compile_run_id
    assert rebuilt.lineage.parent_artifact_ids[-1] == compiled.artifact_id
    assert rebuilt.lineage.compile_run_id != compiled.lineage.compile_run_id
