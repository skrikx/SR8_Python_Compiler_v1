# Diff and Lint

## Diff

`sr8 diff` performs semantic comparison between canonical artifacts.

Command:

```bash
sr8 diff <left-artifact-or-id> <right-artifact-or-id> [--path .sr8]
```

Change classes:

- `added`
- `removed`
- `modified`
- `unchanged`

Impact levels:

- `low`
- `medium`
- `high`

Output includes report ID, refs, summary, and changed field rows.

## Lint

`sr8 lint` evaluates artifact quality with explicit rules.

Command:

```bash
sr8 lint <artifact-or-id> [--path .sr8]
```

Rule coverage:

- `L001` to `L010`
- objective quality
- scope quality
- constraint and success coverage
- scope/exclusion contradiction
- profile signal checks
- transform quality readiness
- authority requirements for procedure-class artifacts
- ambiguity fallback checks

Lint output includes report ID, status (`pass`, `warn`, `fail`), summary, and findings.
Lint is read-only and does not mutate artifacts.
