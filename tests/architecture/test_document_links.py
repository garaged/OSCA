import re
from pathlib import Path

_LINK = re.compile(r"\[[^]]*]\(([^)]+)\)")


def test_repository_markdown_relative_links_resolve() -> None:
    failures: list[str] = []
    for document in Path(".").rglob("*.md"):
        if any(part in {".venv", "node_modules"} for part in document.parts):
            continue
        text = document.read_text(encoding="utf-8")
        for target in _LINK.findall(text):
            path = target.split("#", 1)[0]
            if not path or "://" in path or path.startswith("mailto:"):
                continue
            resolved = (document.parent / path).resolve()
            if not resolved.exists():
                failures.append(f"{document}: {target}")
    assert failures == []
