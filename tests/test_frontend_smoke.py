import json
from pathlib import Path


def test_frontend_package_and_shell_exist() -> None:
    package = json.loads(Path("frontend/package.json").read_text(encoding="utf-8"))

    assert package["name"] == "sr8-frontend"
    assert "check" in package["scripts"]
    assert "build" in package["scripts"]

    app_shell = Path("frontend/src/lib/components/layout/AppShell.svelte")
    sidebar = Path("frontend/src/lib/components/layout/Sidebar.svelte")
    topbar = Path("frontend/src/lib/components/layout/Topbar.svelte")

    assert app_shell.exists()
    assert sidebar.exists()
    assert topbar.exists()
