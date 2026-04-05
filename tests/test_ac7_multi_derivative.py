from sr8.compiler import CompileConfig, compile_intent, recompile_artifact
from sr8.transform.engine import transform_artifact


def test_ac7_three_derivatives_from_one_artifact() -> None:
    base = compile_intent(
        "tests/fixtures/product_prd.md",
        config=CompileConfig(profile="prd"),
    ).artifact
    plan = recompile_artifact(base, profile="plan")
    prompt = recompile_artifact(base, profile="prompt_pack")
    d1 = transform_artifact(base, "markdown_prd").derivative
    d2 = transform_artifact(plan, "markdown_plan").derivative
    d3 = transform_artifact(prompt, "markdown_prompt_pack").derivative
    assert d1.lineage.parent_source_hash == base.source.source_hash
    assert d2.lineage.parent_source_hash == base.source.source_hash
    assert d3.lineage.parent_source_hash == base.source.source_hash
