# CLI Reference

All commands are exposed through `sr8`.

## Global

```bash
sr8 --help
sr8 version
```

## `sr8 init`

Initialize local workspace.

```bash
sr8 init [--path .sr8]
```

## `sr8 compile`

Compile source into canonical artifact.

```bash
sr8 compile <source> [--profile generic] [--source-type text|markdown|json|yaml] [--format json|yaml] [--out <dir>]
```

Notes:

- if `--out` is inside a `.sr8` workspace, compile also writes catalog and receipt records
- otherwise artifact files are written directly to the provided output directory

## `sr8 validate`

Validate existing artifact file.

```bash
sr8 validate <artifact-path> [--profile <profile>]
```

## `sr8 inspect`

Inspect either an artifact file or source input.

```bash
sr8 inspect <artifact-or-source>
```

## `sr8 transform`

Render derivative markdown output from canonical artifact.

```bash
sr8 transform <artifact-path> --to <target> [--out <dir>]
```

## `sr8 diff`

Semantic compare between canonical artifacts (path or ID).

```bash
sr8 diff <left-artifact-or-id> <right-artifact-or-id> [--path .sr8]
```

## `sr8 lint`

Run lint rules against canonical artifact (path or ID).

```bash
sr8 lint <artifact-or-id> [--path .sr8]
```

## `sr8 list`

List catalog records in workspace.

```bash
sr8 list [--kind canonical|derivative] [--profile <profile>] [--path .sr8]
```

## `sr8 show`

Show a catalog record by record ID or artifact ID.

```bash
sr8 show <record-or-artifact-id> [--path .sr8]
```

## Supported Profiles

- `generic`
- `prd`
- `repo_audit`
- `plan`
- `research_brief`
- `procedure`
- `media_spec`
- `prompt_pack`

## Supported Transform Targets

- `markdown_prd`
- `markdown_plan`
- `markdown_research_brief`
- `markdown_procedure`
- `markdown_prompt_pack`
