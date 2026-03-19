# Diff and Lint

## Diff

`sr8 diff` compares semantic fields and classifies changes:
- classes: `added`, `removed`, `modified`, `unchanged`
- impact: `low`, `medium`, `high`

## Lint

`sr8 lint` runs explicit rules `L001` to `L010` for quality and contradiction signals.

Lint does not mutate artifacts.
