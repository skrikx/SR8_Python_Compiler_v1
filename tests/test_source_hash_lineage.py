from sr8.compiler import (
    CompileConfig,
    compile_intent,
    load_source,
    normalize_source,
    recompile_artifact,
)
from sr8.utils.hash import stable_text_hash


def test_recompile_preserves_source_hash_and_parent() -> None:
    compiled = compile_intent(
        "tests/fixtures/product_prd.md",
        config=CompileConfig(profile="prd"),
    ).artifact
    rebuilt = recompile_artifact(compiled, profile="whitepaper_outline")
    assert rebuilt.source.source_hash == compiled.source.source_hash
    assert rebuilt.lineage.source_hash == compiled.source.source_hash
    assert rebuilt.lineage.parent_artifact_ids[-1] == compiled.artifact_id


def test_normalization_preserves_ingest_hash() -> None:
    loaded = load_source("```\nObjective: Build tool\nScope:\n- Parse\n```")
    normalized = normalize_source(loaded)

    assert normalized.source_hash == loaded.source_hash
    assert normalized.metadata["normalized_source_hash"] == stable_text_hash(
        normalized.normalized_content
    )
