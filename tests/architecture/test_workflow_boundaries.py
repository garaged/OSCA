import ast
from pathlib import Path


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_workflow_public_domain_and_application_do_not_import_private_infrastructure() -> None:
    root = Path("src/osca/workflow")
    governed = [
        *root.joinpath("api").glob("*.py"),
        *root.joinpath("domain").glob("*.py"),
        *root.joinpath("application").glob("*.py"),
    ]
    violations = {
        str(path): sorted(
            name for name in imports(path) if name.startswith("osca.workflow.infrastructure")
        )
        for path in governed
        if any(name.startswith("osca.workflow.infrastructure") for name in imports(path))
    }
    assert violations == {}


def test_workflow_handler_does_not_import_other_capability_infrastructure() -> None:
    names = imports(Path("src/osca/workflow/infrastructure/executor.py"))
    private = {
        name
        for name in names
        if name.startswith(
            (
                "osca.catalog.infrastructure",
                "osca.operations.infrastructure",
                "osca.security.infrastructure",
            )
        )
    }
    assert private == set()
