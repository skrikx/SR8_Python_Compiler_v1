# Evaluation Rubrics

SR8 benchmark reports score each case across six dimensions.

## Dimensions

- `faithfulness` - whether the artifact preserves what the input actually said
- `completeness` - whether expected fields are populated for the target profile
- `constraint_integrity` - whether constraints, exclusions, and control conditions survive compilation
- `readiness` - whether validation and lint indicate the result is usable downstream
- `trust_surface` - whether extraction confidence and governance behavior match the input quality
- `transform_utility` - whether required downstream derivatives are generated successfully

## Source of truth

- Case metadata lives in `benchmarks/corpus/<suite>/*.case.json`
- Typed expectations live in `benchmarks/expected/*.json`
- Rubric defaults live in `benchmarks/rubrics/default.json`

## Scoring model

- Each dimension is scored from `0.0` to `1.0`
- Default passing threshold is `0.65`
- The aggregate case score is the mean of the six dimension scores
- A case passes only when every dimension meets the rubric threshold

## Honest interpretation

- A high score means the current heuristic expectations were met.
- A low score means the case should be investigated, not hidden.
- Weak or contradictory inputs should often score lower on readiness while still scoring well on trust surface if SR8 reports the weakness honestly.
