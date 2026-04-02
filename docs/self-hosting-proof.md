# Self-Hosting Proof

WF12 adds an explicit self-hosting benchmark track for SR8.

## Proof cases

- `sr8_workflow_compile` - compile an SR8 workflow specification into a canonical artifact
- `sr8_release_transform` - transform one SR8 canonical artifact into three downstream outputs
- `sr8_recompile_whitepaper` - recompile an SR8 artifact into `whitepaper_outline`
- `sr8_artifact_eval` - evaluate an SR8-generated artifact through the benchmark harness

## Commands

```bash
sr8 benchmark run --suite self_hosting --out ./benchmarks/results/
sr8 benchmark run --all --out ./benchmarks/results/
```

## What this proves

- SR8 can compile documentation about its own evolution into canonical artifacts.
- SR8 can generate downstream derivatives from those artifacts.
- SR8 can use an existing canonical artifact as source and preserve a meaningful recompile path.
- SR8 can score its own artifact outputs with the same rubric-backed harness used elsewhere.

## What this does not prove

- It does not prove human-level evaluation quality.
- It does not prove model-assisted extraction quality because rule-first extraction remains the default path.
- It does not imply hosted telemetry, annotation tooling, or SaaS evaluation infrastructure.
