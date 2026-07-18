from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import Engine

from osca import __version__
from osca.bootstrap.database import SessionProvider, create_sqlite_engine
from osca.operations.infrastructure import (
    SqliteAuditRepository,
    SqliteWorkflowEventRepository,
    configure_telemetry,
)
from osca.workflow.application import WorkflowService
from osca.workflow.infrastructure import SqliteDiagnosticRunRepository
from osca.workflow.infrastructure.observation import WorkflowObserver


@lru_cache(maxsize=1)
def workflow_engine() -> Engine:
    path = Path(os.environ.get("OSCA_DATABASE_PATH", "osca.db"))
    return create_sqlite_engine(path)


@contextmanager
def workflow_service() -> Iterator[WorkflowService]:
    with SessionProvider(workflow_engine()).transaction() as session:
        yield WorkflowService(
            SqliteDiagnosticRunRepository(session),
            WorkflowObserver(
                audit=SqliteAuditRepository(session),
                events=SqliteWorkflowEventRepository(session),
                telemetry=configure_telemetry(service_version=__version__),
            ),
        )
