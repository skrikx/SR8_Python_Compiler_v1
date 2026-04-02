# README Badge Plan

This file defines the live badge surface used in `README.md`.

## Active README Badges

```md
[![CI](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/ci.yml)
[![Docs Check](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/docs-check.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/docs-check.yml)
[![Frontend CI](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/frontend-ci.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/frontend-ci.yml)
[![Hygiene](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/hygiene.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/hygiene.yml)
[![Release](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/release.yml/badge.svg)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/release.yml)
[![CodeQL](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/skrikx/SR8_Python_Compiler_v1/actions/workflows/codeql.yml)
[![GitHub Release](https://img.shields.io/github/v/release/skrikx/SR8_Python_Compiler_v1)](https://github.com/skrikx/SR8_Python_Compiler_v1/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
```

## Badge Rules

1. Only expose badges for workflows with stable names and real gates.
2. Badge links must target the live repository slug and real workflow files.
3. Badged workflows should support manual dispatch so maintainers can recover badge state without synthetic commits.
4. Do not expose a dependency-review badge because that workflow is pull-request scoped and does not provide a stable default-branch signal.
5. Do not expose a PyPI badge until the package is actually published publicly.
