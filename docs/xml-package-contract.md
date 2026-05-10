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
