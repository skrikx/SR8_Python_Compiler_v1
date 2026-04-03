# XML Package Contract

SR8 emits XML package outputs for chat-native delivery targets. The outputs are deterministic, hygiene-safe, and backed by canonical artifacts.

## Package Types

- `promptunit_package` - primary XML package for compiled intent.
- `sr8_prompt` - concise child prompt output.
- `safe_alternative_package` - governance-aware package when safe alternatives are required.

## Output Expectations

- All XML outputs include UTF-8 declarations.
- Output text is escaped and control characters are stripped.
- Governance status is explicit in package metadata.

## Transform Targets

These XML outputs are available as transform targets:

- `xml_promptunit_package`
- `xml_sr8_prompt`
- `xml_safe_alternative_package`

The renderers are thin wrappers around the front door XML renderers to ensure consistency with chat compile packages.
