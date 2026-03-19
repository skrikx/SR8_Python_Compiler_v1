from pathlib import Path

from sr8.io.exporters import load_artifact


def test_examples_inputs_exist() -> None:
    assert Path("examples/founder_ask.md").exists()
    assert Path("examples/product_prd.md").exists()
    assert Path("examples/repo_audit.md").exists()


def test_examples_outputs_roundtrip() -> None:
    generic = load_artifact("examples/outputs/canonical_generic.json")
    prd = load_artifact("examples/outputs/canonical_prd.json")
    prd_md = Path("examples/outputs/markdown_prd.md").read_text(encoding="utf-8")
    plan_md = Path("examples/outputs/markdown_plan.md").read_text(encoding="utf-8")
    assert generic.artifact_id.startswith("art_")
    assert prd.profile == "prd"
    assert prd_md.startswith("# PRD")
    assert plan_md.startswith("# Plan")
