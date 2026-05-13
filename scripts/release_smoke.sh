#!/usr/bin/env bash
set -u

mkdir -p proof
LOG="$(pwd)/proof/release-smoke.log"
: > "$LOG"

run_step() {
  echo "\$ $*" | tee -a "$LOG"
  if "$@" >> "$LOG" 2>&1; then
    echo "PASS $*" | tee -a "$LOG"
  else
    code=$?
    echo "FAIL($code) $*" | tee -a "$LOG"
    return "$code"
  fi
}

run_step python -m pip install -e ".[dev]"
run_step sr8 version
run_step sr8 --help
run_step python -m sr8.cli --help
run_step python -m pytest
run_step python -m ruff check .
run_step python -m mypy src
run_step sr8 schema export --out schemas/intent_artifact.schema.json
run_step sr8 proof run examples/product_prd.md --profile prd --mode rules --out proof/sr8-v1-local-proof/rules_baseline
run_step sr8 benchmark run --suite rules_required --out proof/benchmark/rules_required

if [ -d frontend ]; then
  (
    cd frontend &&
    run_step npm ci &&
    run_step npm run check &&
    run_step npm run build
  )
fi
