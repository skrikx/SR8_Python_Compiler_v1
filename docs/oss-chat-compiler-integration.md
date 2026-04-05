# OSS Chat Compiler Integration

WF19 absorbs the OSS chat compiler assets into SR8 as architectural references and acceptance fixtures. The OSS assets are not a parallel runtime and do not replace the SR8 compiler nucleus.

## Asset Locations

- `specs/SROS_SELF_COMPILER_SPEC.v3.xml`
- `intake/COMPILER_INPUT_FORM.xml`
- `rules/XML_HYGIENE_RULES.md`
- `examples/chat_frontdoor/`
- `examples/demo_agents/`

## Role

- Specs and intake forms define front door contracts and fallback behavior.
- XML hygiene rules inform render and validation constraints.
- Demo agents remain examples and fixtures only.

SR8 front door behavior terminates in canonical artifacts before emitting XML packages.
