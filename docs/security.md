# Security

SR8 security posture is built on automated repository checks plus private disclosure for vulnerabilities.

## Automated Security Controls

- Dependency review:
  - `.github/workflows/dependency-review.yml`
  - Runs on every pull request and blocks high-severity dependency risk.
- Code scanning:
  - `.github/workflows/codeql.yml`
  - Runs on pull requests to `main`, pushes to `main`, and weekly schedule.
- Dependabot:
  - `.github/dependabot.yml`
  - Weekly updates for Python dependencies and GitHub Actions dependencies.
- CI quality gates:
  - `.github/workflows/ci.yml`
  - Lint, typecheck, tests, examples smoke, and package build smoke on pull requests.

## API Runtime Boundaries

- Trusted-local by default:
  - Workspace override is denied unless explicitly enabled through runtime settings.
  - Multi-tenant workspace access is denied by default.
- Auth-ready hooks:
  - Setting `SR8_API_AUTH_TOKEN` turns on bearer-token checks for non-safe routes.
  - Safe routes such as `/health` remain available without auth.
- Rate-limit hook:
  - `SR8_API_RATE_LIMIT_REQUESTS` and `SR8_API_RATE_LIMIT_WINDOW_SECONDS` enable a process-local fixed-window limiter.
- Compile budget controls:
  - `SR8_API_MAX_SOURCE_CHARS` bounds inline source size.
  - `SR8_API_MAX_PAYLOAD_NODES` bounds structured payload size.
- Concurrency and replay:
  - `SR8_API_MAX_CONCURRENT_OPERATIONS` bounds compile concurrency.
  - Async compile jobs and idempotency keys prevent duplicate execution drift in the local runtime model.

## Supply Chain Notes

- Release publishing uses PyPI Trusted Publishing via OIDC in `.github/workflows/release.yml`.
- The publish job requires `id-token: write` and does not rely on static PyPI API tokens.
- Release artifacts (sdist and wheel) are built in CI and attached to GitHub Releases.

## Vulnerability Disclosure

For security-sensitive findings, use GitHub Security Advisories for private reporting in this repository.
Do not open a public issue for exploit details.

For non-sensitive hardening ideas, open a standard issue using the repository issue templates.

## Maintainer Handling Expectations

1. Acknowledge private reports quickly and reproduce in a local environment.
2. Scope impact and affected versions.
3. Land fix and tests through normal CI gates.
4. Cut a patched release tag and publish through the release workflow.
5. Publish advisory details after a fix is available.
