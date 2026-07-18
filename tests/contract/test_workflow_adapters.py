import json
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from osca.bootstrap.cli import app as cli_app
from osca.bootstrap.web import app as web_app
from osca.bootstrap.workflow import workflow_engine


def migrate(path: Path) -> None:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{path}")
    command.upgrade(config, "head")


def test_http_and_cli_observe_semantically_equivalent_run(
    tmp_path: Path, monkeypatch: object
) -> None:
    database = tmp_path / "adapters.db"
    migrate(database)
    monkeypatch.setenv("OSCA_DATABASE_PATH", str(database))  # type: ignore[attr-defined]
    workflow_engine.cache_clear()

    submitted = TestClient(web_app).post(
        "/api/v1/diagnostic-runs",
        json={
            "actor": "operator",
            "correlation_id": {},
            "idempotency_key": "adapter-fixture",
            "input": {"probe": "storage"},
        },
    )
    assert submitted.status_code == 201
    api_run = submitted.json()
    cli = CliRunner().invoke(cli_app, ["diagnostic-get", api_run["run_id"]["value"]])
    assert cli.exit_code == 0
    cli_run = json.loads(cli.stdout)
    for field in ("run_id", "state", "attempt", "checkpoint", "error"):
        assert cli_run[field] == api_run[field]
