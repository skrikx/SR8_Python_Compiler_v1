from pathlib import Path


def test_frontend_routes_exist() -> None:
    required_routes = [
        "frontend/src/routes/+page.svelte",
        "frontend/src/routes/compile/+page.svelte",
        "frontend/src/routes/artifacts/+page.svelte",
        "frontend/src/routes/artifacts/[id]/+page.svelte",
        "frontend/src/routes/transforms/+page.svelte",
        "frontend/src/routes/diff/+page.svelte",
        "frontend/src/routes/lint/+page.svelte",
        "frontend/src/routes/receipts/+page.svelte",
        "frontend/src/routes/benchmarks/+page.svelte",
        "frontend/src/routes/providers/+page.svelte",
        "frontend/src/routes/settings/+page.svelte",
    ]

    for route in required_routes:
        assert Path(route).exists(), route


def test_compile_and_providers_routes_bind_to_api_surfaces() -> None:
    compile_server = Path("frontend/src/routes/compile/+page.server.ts").read_text(encoding="utf-8")
    providers_server = Path("frontend/src/routes/providers/+page.server.ts").read_text(
        encoding="utf-8"
    )

    assert "client.compile" in compile_server
    assert "client.providers()" in compile_server
    assert "client.providers()" in providers_server
    assert "client.providerProbe()" in providers_server
