from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from osca.bootstrap.runtime import readiness_snapshot
from osca.operations.api import ReadinessSnapshot

app = FastAPI(title="OSCA", version="0.1.0", openapi_version="3.1.0")


@app.get("/api/v1/readiness", response_model=ReadinessSnapshot)
def api_readiness() -> ReadinessSnapshot:
    return readiness_snapshot()


@app.get("/health", response_class=HTMLResponse)
def web_readiness() -> str:
    snapshot = readiness_snapshot()
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>OSCA readiness</title></head><body><main>"
        f"<h1>OSCA readiness</h1><p data-state='{snapshot.state.value}'>"
        f"State: {snapshot.state.value}</p><p>Version: {snapshot.product_version}</p>"
        "</main></body></html>"
    )

