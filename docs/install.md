# Install

SR8 is designed to clone clean, install clean, and run locally with minimal setup.

## Requirements

- Python `>=3.11`
- Node.js `>=20` for the frontend checks only

## Editable Install

```bash
python -m pip install -e .
```

## Development Install

```bash
python -m pip install -e ".[dev]"
```

## Frontend Install

Frontend tooling is only required when you want to validate the local web surface.

```bash
cd frontend
npm ci
```

## Optional Local Env File

SR8 loads settings from process environment plus these optional repo-root files:

- `.env`
- `.env.local`

Start from `.env.example`. Keep real secrets in local env files only.

## Install Verification

```bash
sr8 --help
sr8 version
python -m build
```

## Optional API Runtime

```bash
uvicorn sr8.api.app:app --reload
```

Then open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
