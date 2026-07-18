import ast
from pathlib import Path


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_recovery_public_domain_and_application_do_not_import_private_capabilities() -> None:
    root = Path("src/osca/recovery")
    governed = [
        *root.joinpath("api").glob("*.py"),
        *root.joinpath("domain").glob("*.py"),
        *root.joinpath("application").glob("*.py"),
    ]
    private_prefixes = (
        "osca.catalog.infrastructure",
        "osca.operations.infrastructure",
        "osca.security.infrastructure",
        "osca.workflow.infrastructure",
    )
    violations = {
        str(path): sorted(
            name for name in _imports(path) if name.startswith(private_prefixes)
        )
        for path in governed
        if any(name.startswith(private_prefixes) for name in _imports(path))
    }
    assert violations == {}
