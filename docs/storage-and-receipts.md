# Storage and Receipts

SR8 persistence is local and workspace-based.

## Workspace Structure

Default workspace root: `.sr8`

- canonical artifacts: `.sr8/artifacts/canonical/`
- derivative artifacts: `.sr8/artifacts/derivative/`
- compile receipts: `.sr8/receipts/compile/`
- transform receipts: `.sr8/receipts/transform/`
- catalog index: `.sr8/index/catalog.json`
- temporary files: `.sr8/tmp/`

## Workspace Initialization

`sr8 init` creates the full directory tree and an empty catalog.

## Canonical Save Behavior

When compiling to a `.sr8` path:

- writes unique canonical artifact file
- writes `latest.json`
- appends catalog record
- writes compile receipt

## Derivative Save Behavior

When transforming to a `.sr8` path:

- writes unique derivative JSON and markdown files
- writes `latest.json` and `latest.md`
- appends catalog record
- writes transform receipt

## Catalog Usage

- `sr8 list` reads filtered catalog records
- `sr8 show` resolves by record ID or artifact ID
- `sr8 diff` and `sr8 lint` can resolve canonical artifacts by ID using workspace path

## Collision Handling

Storage path helpers preserve existing files and generate unique suffixes when collisions occur.
