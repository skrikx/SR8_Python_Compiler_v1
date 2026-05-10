# XML Package Contract

SR8 emits XML package outputs for chat-native delivery targets. The outputs are deterministic, hygiene-safe, and backed by canonical artifacts.

## Package Types

- `promptunit_package` - primary XML package for compiled intent.
- `sr8_prompt` - concise child prompt output.
- `safe_alternative_package` - governance-aware package when safe alternatives are required.
- `SRXML_Artifact` - SRXML v1.0 RC2 artifact surface for governed downstream interchange.

## Output Expectations

- All XML outputs include UTF-8 declarations.
- Output text is escaped and control characters are stripped.
- Governance status is explicit in package metadata.

## Transform Targets

These XML outputs are available as transform targets:

- `xml_promptunit_package`
- `xml_sr8_prompt`
- `xml_safe_alternative_package`
- `xml_srxml_rc2`

The renderers are thin wrappers around the front door XML renderers to ensure consistency with chat compile packages.
The `xml_srxml_rc2` renderer is backed by `sr8.srxml`, which classifies canonical SR8 artifacts into RC2 artifact families, preserves lineage fields, emits D2 validation and receipt sections, and returns a blocked-state receipt when the canonical artifact is incomplete or failed.

## Compile Validation Target

SRXML RC2 is also available as a compile-stage validation target:

```bash
sr8 compile examples/product_prd.md --target xml_srxml_rc2 --validate --out ./.sr8/artifacts/canonical/
```

This path preserves SR8's canonical artifact as the internal AST. Compile then renders the canonical artifact to SRXML RC2, validates that XML with `sr8.srxml.validate_srxml_text`, stores the target validation summary in artifact metadata, and records it in the compile receipt. If SRXML validation fails or the SR8 artifact is incomplete, the compile receipt is rejected and the SRXML output contains a repair or blocked-state receipt.
