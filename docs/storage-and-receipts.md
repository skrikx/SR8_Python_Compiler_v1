# Storage and Receipts

Workspace root defaults to `.sr8`.

Artifacts and receipts are append-only by default:
- Canonical artifacts: `.sr8/artifacts/canonical/`
- Derivative artifacts: `.sr8/artifacts/derivative/`
- Compile receipts: `.sr8/receipts/compile/`
- Transform receipts: `.sr8/receipts/transform/`
- Catalog index: `.sr8/index/catalog.json`

IDs and paths are deterministic with uniqueness suffixes when collisions occur.
