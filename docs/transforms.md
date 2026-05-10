# Transforms

SR8 transforms render derivative artifacts from canonical artifacts.

## Built-in Targets

- `markdown_prd`
- `markdown_plan`
- `markdown_research_brief`
- `markdown_procedure`
- `markdown_prompt_pack`
- `xml_promptunit_package`
- `xml_sr8_prompt`
- `xml_safe_alternative_package`
- `xml_srxml_rc2`

## Transform Flow

1. Load canonical artifact.
2. Resolve target spec from registry.
3. Check target compatibility with artifact profile.
4. Render text content.
5. Emit `DerivativeArtifact` with lineage.

## CLI Usage

```bash
sr8 transform ./.sr8/artifacts/canonical/latest.json --to markdown_prd --out ./.sr8/artifacts/derivative/
sr8 transform ./.sr8/artifacts/canonical/latest.json --to xml_srxml_rc2 --out ./.sr8/artifacts/derivative/
```

If output path is inside `.sr8`, transform persistence writes derivative record and transform receipt.

## Compile-Stage Target Validation

`xml_srxml_rc2` is not limited to passive transform export. It can be requested during compile:

```bash
sr8 compile examples/product_prd.md --target xml_srxml_rc2 --validate --out ./.sr8/artifacts/canonical/
```

The compile path still produces a canonical SR8 artifact first. It then renders SRXML RC2, validates the rendered XML, writes `latest_xml_srxml_rc2.xml` when `--out` is provided, and rejects the compile receipt when the SRXML target is invalid or blocked.

## Failure Modes

Transform returns explicit errors for:

- unknown target
- profile-target incompatibility

## Extension

See [transform-authoring.md](transform-authoring.md) for adding new transform targets.
