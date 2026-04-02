# Benchmarking

SR8 v1.2 adds a local-first evaluation lab for repeatable benchmark runs.

## Scope

- Founder intent
- Research intent
- Repo and engineering intent
- Operational procedure intent
- Weak and contradictory intent
- Self-hosting SR8 proof cases

## Commands

```bash
sr8 benchmark run --suite founder
sr8 benchmark run --suite self_hosting --out ./benchmarks/results/
sr8 benchmark run --all --out ./benchmarks/results/
sr8 benchmark compare baseline.json candidate.json --out ./benchmarks/results/
```

## What a run does

For each benchmark case, SR8:

1. Compiles the input source or recompiles an existing artifact.
2. Runs validation and lint.
3. Executes configured transforms when the case requires derivative proof.
4. Scores the result against typed expectations.
5. Writes JSON and Markdown reports for later comparison.

## Output pack

- `benchmarks/results/<suite>.json` - machine-readable results
- `benchmarks/results/<suite>.md` - readable summary
- `benchmarks/results/latest.json` - latest run snapshot

## Score meaning

Scores are deterministic heuristics backed by explicit expectations in `benchmarks/expected/`.
They are useful for regression detection and failure clustering.
They are not human-judgment replacements and should not be presented as absolute quality truth.

## Limits

- The benchmark corpus is intentionally small and curated. It is a proof pack, not a universal evaluation set.
- Scores depend on current rule-first extraction behavior and current profile validations.
- Weak-input performance is expected to surface warnings and lower readiness rather than polished output.
