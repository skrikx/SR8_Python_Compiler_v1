# Founder Intent

Objective:
- Build a local-first intent compiler core for SR8.

Scope:
- Ingest text, markdown, json, and yaml.
- Assemble a canonical intent artifact.
- Expose a compile_intent Python API.

Exclusions:
- No full profile overlay in this phase.
- No polished CLI compile UX in this phase.

Constraints:
- Python 3.12+
- Deterministic rule-first extraction.
- No required LLM dependency.

Assumptions:
- Inputs can be ambiguous.
- Ambiguity should be preserved when signal is weak.

Dependencies:
- pydantic v2
- typer
- pytest

Success Criteria:
- compile_intent returns artifact and receipt.
- Canonical artifact includes lineage and source hash.

Output Contract:
- Return artifact
- Return receipt
- Return normalized source
- Return extracted dimensions

Target Class:
- compiler_core

Authority Context:
- founder
