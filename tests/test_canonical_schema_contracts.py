import json

from sr8.compiler import compile_intent


def test_canonical_artifact_contract_is_complete() -> None:
    artifact = compile_intent("tests/fixtures/input_founder_ask.md").artifact
    payload = artifact.model_dump(mode="json")

    assert {
        "artifact_id",
        "artifact_version",
        "compiler_version",
        "profile",
        "created_at",
        "source",
        "objective",
        "scope",
        "exclusions",
        "constraints",
        "context_package",
        "target_class",
        "authority_context",
        "dependencies",
        "assumptions",
        "success_criteria",
        "output_contract",
        "governance_flags",
        "validation",
        "lineage",
        "metadata",
    }.issubset(payload.keys())
    assert {"source_id", "source_type", "source_hash", "origin"} == set(payload["source"].keys())
    assert {
        "compile_run_id",
        "pipeline_version",
        "source_hash",
        "parent_source_hash",
        "parent_compile_run_id",
        "steps",
        "parent_artifact_ids",
    }.issubset(payload["lineage"].keys())
    assert "extraction_trace" in payload["metadata"]
    assert "extraction_trust_summary" in payload["metadata"]
    assert "weak_intent_recovery" in payload["metadata"]
    assert "compile_kind" in payload["metadata"]
    assert "semantic_transform_applied" in payload["metadata"]
    assert "source_structure_kind" in payload["metadata"]
    assert "source_supplied_fields" in payload["metadata"]
    assert "compiler_derived_fields" in payload["metadata"]
    assert "unresolved_fields" in payload["metadata"]
    assert "compile_truth_summary" in payload["metadata"]


def test_canonical_artifact_contract_round_trips_as_json() -> None:
    artifact = compile_intent("Objective: Stable contract\nScope:\n- parser\n").artifact
    encoded = json.dumps(artifact.model_dump(mode="json"), sort_keys=True)
    decoded = json.loads(encoded)

    assert decoded["artifact_id"] == artifact.artifact_id
    assert decoded["source"]["source_hash"] == artifact.source.source_hash
    assert decoded["lineage"]["compile_run_id"] == artifact.lineage.compile_run_id
