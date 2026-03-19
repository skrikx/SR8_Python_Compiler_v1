# Installation

## Python Requirement

SR8 requires Python `>=3.12`.

## Editable Install

```bash
python -m pip install -e .
```

## Development Install

```bash
python -m pip install -e ".[dev]"
```

## Validate Installation

```bash
sr8 --help
sr8 version
```

## Optional API Runtime

SR8 includes a FastAPI app entrypoint:

```bash
uvicorn sr8.api.app:app --reload
```

Then open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
