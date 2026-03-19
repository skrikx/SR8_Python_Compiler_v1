# SR8 v1.0.0 First Release Notes (Draft)

## Summary

SR8 v1.0.0 is the first public release of a local-first intent compiler for canonical artifact generation, transform rendering, and quality analysis.

## Added

- canonical compile pipeline with ingest, normalize, extract, and assembly
- profile overlays (`generic`, `prd`, `repo_audit`, `plan`, `research_brief`, `procedure`, `media_spec`, `prompt_pack`)
- transform targets (`markdown_prd`, `markdown_plan`, `markdown_research_brief`, `markdown_procedure`, `markdown_prompt_pack`)
- local workspace persistence with catalog and receipts
- semantic diff and lint reporting
- FastAPI service surface (`/health`, `/compile`, `/validate`, `/transform`)
- CI, release automation, dependency review, and code scanning workflows
- public OSS docs, contributor docs, governance docs, and maintainer baseline docs

## Changed

- repository now includes release checklist, launch assets, and triage documentation baseline

## Security

- dependency review workflow on pull requests
- CodeQL scanning on push, pull request, and schedule
- documented private vulnerability reporting path

## Upgrade Notes

- Requires Python 3.12 or newer.
- Release publishing path uses trusted publishing (OIDC) in GitHub Actions.
