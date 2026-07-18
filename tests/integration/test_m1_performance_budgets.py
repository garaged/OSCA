from __future__ import annotations

import subprocess
import sys
from statistics import quantiles
from time import perf_counter

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.bootstrap.authorization import local_authorization_context
from osca.bootstrap.runtime import readiness_snapshot
from osca.catalog.infrastructure import CatalogBase, SqliteResultCatalog
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import CancelDiagnosticRun, DiagnosticInput, SubmitDiagnosticRun
from osca.workflow.application import WorkflowService
from osca.workflow.infrastructure import SqliteDiagnosticRunRepository, WorkflowBase
from osca.workflow.infrastructure.executor import EmbeddedExecutor


def elapsed(operation: object) -> float:
    started = perf_counter()
    operation()  # type: ignore[operator]
    return perf_counter() - started


def command(key: str) -> SubmitDiagnosticRun:
    return SubmitDiagnosticRun(
        authorization=local_authorization_context(),
        correlation_id=CorrelationId.new(),
        idempotency_key=key,
        input=DiagnosticInput(probe="storage"),
    )


def test_reference_environment_m1_performance_budgets() -> None:
    """Verify M1-AC-019 targets as bounded reference-environment observations."""

    startup = elapsed(
        lambda: subprocess.run(
            [sys.executable, "-c", "import osca.bootstrap.web"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
    )
    readiness_samples = [elapsed(readiness_snapshot) for _ in range(100)]
    readiness_p95 = quantiles(readiness_samples, n=100)[94]

    engine = create_engine("sqlite://")
    WorkflowBase.metadata.create_all(engine)
    CatalogBase.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        repository = SqliteDiagnosticRunRepository(session)
        service = WorkflowService(repository)

        started = perf_counter()
        submitted = service.submit(command("performance-submit"))
        submission = perf_counter() - started

        started = perf_counter()
        visible = repository.get(submitted.run_id)
        visibility = perf_counter() - started
        assert visible is not None

        worker = EmbeddedExecutor(
            repository,
            owner="performance-observer",
            result_catalog=SqliteResultCatalog(session),
        )
        claimed = worker.claim()
        assert claimed is not None
        started = perf_counter()
        completed = worker.execute(claimed)
        progress = perf_counter() - started
        assert completed.checkpoint is not None and completed.checkpoint.phase == 3

        pending = service.submit(command("performance-cancel"))
        started = perf_counter()
        service.cancel(
            CancelDiagnosticRun(
                authorization=local_authorization_context(),
                correlation_id=CorrelationId.new(),
                run_id=pending.run_id,
            )
        )
        cancellation = perf_counter() - started

    observations = {
        "startup_seconds": startup,
        "readiness_p95_seconds": readiness_p95,
        "submission_seconds": submission,
        "visibility_seconds": visibility,
        "progress_seconds": progress,
        "cancellation_seconds": cancellation,
    }
    assert observations["startup_seconds"] < 5
    assert observations["readiness_p95_seconds"] < 1
    assert observations["submission_seconds"] < 1
    assert observations["visibility_seconds"] < 5
    assert observations["progress_seconds"] < 2
    assert observations["cancellation_seconds"] < 2
    pytest.record_property("m1_performance_observations", observations)  # type: ignore[attr-defined]
