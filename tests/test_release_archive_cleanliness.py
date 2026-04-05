from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_root_gitignore_covers_local_runtime_and_audit_outputs() -> None:
    gitignore = _read(".gitignore")
    for pattern in (
        "artifacts/*",
        "!artifacts/.gitkeep",
        "receipts/*",
        "!receipts/.gitkeep",
        ".sr8/",
        "runs/",
        "benchmarks/results/",
        "examples/outputs/art_*.json",
        "examples/outputs/latest.json",
        "examples/outputs/latest.md",
        "*.log",
        "*.zip",
        "*_audit.md",
        "sr8_v1_compiler_first_run.txt",
    ):
        assert pattern in gitignore


def test_frontend_gitignore_covers_local_build_outputs() -> None:
    gitignore = _read("frontend/.gitignore")
    for pattern in ("node_modules/", ".npm-cache/", ".svelte-kit/", "build/", "dist/"):
        assert pattern in gitignore


def test_examples_docs_mark_transient_outputs_as_rebuildable() -> None:
    examples = _read("docs/examples.md").lower()
    assert "rebuildable local outputs" in examples
    assert "transient `art_*.json` and `latest.*` files" in examples


def test_placeholder_output_directories_are_clean() -> None:
    for directory in (Path("artifacts"), Path("receipts")):
        names = sorted(path.name for path in directory.iterdir())
        assert names == [".gitkeep"], (directory, names)


def test_release_noise_files_are_absent_or_export_ignored() -> None:
    gitattributes = _read(".gitattributes")
    pyproject = _read("pyproject.toml")
    ignored = "SR8_Compiler_v1_Workflows.zip export-ignore"
    assert ignored in gitattributes
    assert "/SR8_Compiler_v1_Workflows.zip" in pyproject
    assert "/examples/outputs/art_*.json" in pyproject
    assert not Path("SR8_updated_zip_audit.md").exists()
    assert not Path("sr8_v1_compiler_first_run.txt").exists()
    assert not Path("runs").exists()
