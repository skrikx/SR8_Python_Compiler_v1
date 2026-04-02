from __future__ import annotations

from sr8.eval.types import RubricDefinition, RubricDimension

DEFAULT_RUBRIC = RubricDefinition(
    rubric_id="wf12.default",
    name="WF12 Benchmark Rubric",
    dimensions=[
        RubricDimension(
            dimension="faithfulness",
            question="Did the artifact preserve what the input actually said?",
            passing_score=0.65,
            weight=1.0,
        ),
        RubricDimension(
            dimension="completeness",
            question="Did the artifact capture the expected dimensions for the target profile?",
            passing_score=0.65,
            weight=1.0,
        ),
        RubricDimension(
            dimension="constraint_integrity",
            question="Were constraints, exclusions, authority, and success criteria preserved?",
            passing_score=0.65,
            weight=1.0,
        ),
        RubricDimension(
            dimension="readiness",
            question="Is the output usable for downstream work without major correction?",
            passing_score=0.65,
            weight=1.0,
        ),
        RubricDimension(
            dimension="trust_surface",
            question=(
                "Did confidence, trace, warnings, and lint behave honestly "
                "for the input quality?"
            ),
            passing_score=0.65,
            weight=1.0,
        ),
        RubricDimension(
            dimension="transform_utility",
            question="Do downstream derivatives remain useful and aligned when generated?",
            passing_score=0.65,
            weight=1.0,
        ),
    ],
    notes=[
        (
            "Scores are deterministic heuristics tied to explicit expectations "
            "and current compiler behavior."
        ),
        (
            "These reports are regression-oriented. They support comparison and "
            "failure discovery, not absolute truth claims."
        ),
    ],
)


def get_default_rubric() -> RubricDefinition:
    return DEFAULT_RUBRIC
