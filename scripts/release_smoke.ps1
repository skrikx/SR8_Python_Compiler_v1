$ErrorActionPreference = "Continue"

New-Item -ItemType Directory -Force -Path "proof" | Out-Null
$Log = (Resolve-Path "proof").Path + "\release-smoke.log"
Set-Content -Path $Log -Value "" -Encoding utf8

function Invoke-SmokeStep {
    param([string]$Command)
    Add-Content -Path $Log -Value "`$ $Command" -Encoding utf8
    Invoke-Expression "$Command *>> `"$Log`""
    if ($LASTEXITCODE -eq 0) {
        Add-Content -Path $Log -Value "PASS $Command" -Encoding utf8
    } else {
        Add-Content -Path $Log -Value "FAIL($LASTEXITCODE) $Command" -Encoding utf8
        exit $LASTEXITCODE
    }
}

Invoke-SmokeStep 'python -m pip install -e ".[dev]"'
Invoke-SmokeStep 'sr8 version'
Invoke-SmokeStep 'sr8 --help'
Invoke-SmokeStep 'python -m sr8.cli --help'
Invoke-SmokeStep 'python -m pytest'
Invoke-SmokeStep 'python -m ruff check .'
Invoke-SmokeStep 'python -m mypy src'
Invoke-SmokeStep 'sr8 schema export --out schemas/intent_artifact.schema.json'
Invoke-SmokeStep 'sr8 proof run examples/product_prd.md --profile prd --mode rules --out proof/sr8-v1-local-proof/rules_baseline'
Invoke-SmokeStep 'sr8 benchmark run --suite rules_required --out proof/benchmark/rules_required'

if (Test-Path "frontend") {
    Push-Location frontend
    Invoke-SmokeStep 'npm ci'
    Invoke-SmokeStep 'npm run check'
    Invoke-SmokeStep 'npm run build'
    Pop-Location
}
