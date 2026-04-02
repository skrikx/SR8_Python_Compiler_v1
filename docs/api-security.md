# API Security

SR8's local API is intentionally thinner and stricter than the CLI.

## Compile Input Rules

- `/compile` accepts inline `source_text` or structured `source_payload`.
- `source` remains accepted as a backward-compatible alias for `source_text`.
- Arbitrary local filesystem paths are rejected before they reach compiler ingestion.
- Rejected path inputs return `422` with a structured `path_input_disallowed` error.

## Error Response Shape

Expected API failures use this envelope:

```json
{
  "error": {
    "code": "invalid_artifact_payload",
    "message": "Artifact '.../artifact.json' could not be parsed.",
    "details": {
      "path": ".../artifact.json",
      "reason": "invalid_json"
    }
  }
}
```

## Expected Client Failure Mapping

- Invalid provider name -> `422`
- Missing artifact path -> `404`
- Invalid JSON or YAML artifact payload -> `422`
- Binary or non-UTF-8 artifact content -> `415`
- Unsupported artifact extension on artifact routes -> `422`

Unexpected internal failures remain `500` and do not expose internal stack details.
