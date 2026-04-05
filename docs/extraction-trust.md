# Extraction Trust

SR8 exposes extraction trust through `metadata.extraction_trace`.

Each confidence signal includes:
- field_name
- status
- confidence_band
- evidence_summary
- notes

Statuses include explicit, inferred, weak, empty, and contradictory.
Current rule-based extraction can emit all five statuses deterministically.

Trust output is consumed by:

- `sr8 inspect`
- validation warnings
- lint findings
- compilation receipts

Critical fields currently watched for weak or empty trust:

- `authority_context`
- `dependencies`
- `assumptions`
- `success_criteria`
- `output_contract`
- `context_package`
