from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from osca.analyst_workspace.contracts import (
    AnalystWorkspaceSnapshot,
    WorkspaceSection,
    WorkspaceSectionResult,
)
from osca.analyst_workspace.model_validation import model_validation_router
from osca.analyst_workspace.prediction_lab import prediction_lab_router
from osca.analyst_workspace.quantitative import quantitative_router
from osca.analyst_workspace.services import AnalystWorkspaceService
from osca.analyst_workspace.visualization import visualization_router


def create_app(
    *,
    storage_root: Path = Path(".osca"),
    service: AnalystWorkspaceService | None = None,
) -> FastAPI:
    workspace_service = service or AnalystWorkspaceService()
    root = storage_root.resolve()
    app = FastAPI(
        title="OSCA Analyst Workspace",
        version="1.4.0",
        description=(
            "Read-only local workspace for evidence, charts, analysis, ML diagnostics, "
            "and research validation."
        ),
    )
    app.include_router(visualization_router())
    app.include_router(quantitative_router())
    app.include_router(prediction_lab_router())
    app.include_router(model_validation_router())

    @app.get("/", response_class=HTMLResponse)
    def workspace_page() -> str:
        return _workspace_html()

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "read_only": True,
            "storage_root": str(root),
            "network_access_enabled": False,
            "interactive_visualization_enabled": True,
            "quantitative_analysis_enabled": True,
            "prediction_lab_enabled": True,
            "model_research_validation_enabled": True,
            "automatic_model_promotion_enabled": False,
            "broker_execution_enabled": False,
        }

    @app.get("/api/workspace", response_model=AnalystWorkspaceSnapshot)
    def workspace_snapshot() -> AnalystWorkspaceSnapshot:
        return workspace_service.snapshot(root)

    @app.get(
        "/api/workspace/{section_name}",
        response_model=WorkspaceSectionResult,
    )
    def workspace_section(section_name: str) -> WorkspaceSectionResult:
        try:
            section = WorkspaceSection(section_name)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail="unknown workspace section") from exc
        return workspace_service.section(root, section)

    return app


def _workspace_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OSCA Analyst Workspace</title>
<style>
:root { color-scheme: light dark; font-family: ui-sans-serif, system-ui, sans-serif; }
body { margin: 0; background: #111827; color: #e5e7eb; }
header { padding: 2rem max(1.25rem, 5vw); border-bottom: 1px solid #374151; }
h1 { margin: 0 0 .5rem; font-size: clamp(1.8rem, 4vw, 3rem); }
header p { margin: 0; color: #9ca3af; }
nav { margin-top: 1rem; }
nav a { color: #93c5fd; }
main { padding: 1.5rem max(1.25rem, 5vw) 3rem; }
#status { margin-bottom: 1rem; color: #93c5fd; }
.grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
section { background: #1f2937; border: 1px solid #374151; border-radius: 14px; padding: 1rem; }
section h2 { display: flex; justify-content: space-between; margin: 0 0 .8rem; font-size: 1.05rem; }
.count { color: #93c5fd; }
.item { border-top: 1px solid #374151; padding: .75rem 0; }
.item:first-of-type { border-top: 0; }
.item h3 { margin: 0 0 .3rem; font-size: .98rem; }
.item p, .empty { margin: 0; color: #9ca3af; line-height: 1.45; }
.badge { display: inline-block; margin-top: .45rem; padding: .15rem .45rem; border-radius: 999px; background: #374151; font-size: .75rem; }
.warning { color: #fde68a; }
.error { color: #fca5a5; }
footer { padding: 0 max(1.25rem, 5vw) 2rem; color: #9ca3af; font-size: .85rem; }
</style>
</head>
<body>
<header>
  <h1>OSCA Analyst Workspace</h1>
  <p>Read-only inspection of local datasets, charts, quantitative analysis, ML evidence, and research validation.</p>
  <nav><a href="/charts">Open interactive market-data visualization</a></nav>
</header>
<main>
  <div id="status">Loading retained evidence…</div>
  <div id="workspace" class="grid" aria-live="polite"></div>
</main>
<footer>No recommendations, provider credentials, broker connections, automatic promotion, or order execution.</footer>
<script>
const workspace = document.getElementById('workspace');
const status = document.getElementById('status');
function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}
fetch('/api/workspace')
  .then(response => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then(data => {
    const mode = data.read_only ? 'read-only' : 'writable';
    status.textContent = `${data.total_items} retained items · ${mode}`;
    data.sections.forEach(group => {
      const section = node('section');
      const heading = node('h2');
      heading.append(node('span', group.section.replaceAll('_', ' ')));
      heading.append(node('span', String(group.item_count), 'count'));
      section.append(heading);
      if (group.items.length === 0) section.append(node('p', group.empty_message, 'empty'));
      group.items.forEach(item => {
        const article = node('article', undefined, 'item');
        article.append(node('h3', item.title));
        article.append(node('p', item.summary));
        article.append(node('span', item.status.replaceAll('_', ' '), 'badge'));
        section.append(article);
      });
      workspace.append(section);
    });
    data.warnings.forEach(message => workspace.prepend(node('p', message, 'warning')));
  })
  .catch(error => {
    status.textContent = 'Workspace could not be loaded.';
    status.className = 'error';
    workspace.append(node('p', String(error), 'error'));
  });
</script>
</body>
</html>"""
