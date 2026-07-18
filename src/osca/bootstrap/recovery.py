from __future__ import annotations

import os
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from osca import __version__
from osca.bootstrap.database import create_sqlite_engine
from osca.catalog.infrastructure import SqliteResultCatalog
from osca.configuration.api import ValidatedConfiguration
from osca.configuration.infrastructure import SqliteConfigurationRepository
from osca.operations.infrastructure import SqliteAuditRepository, configure_telemetry
from osca.recovery.application.service import RecoveryService
from osca.recovery.infrastructure import SqliteRecoveryOperationRepository
from osca.recovery.infrastructure.age import AgeProcessContainer
from osca.recovery.infrastructure.observation import RecoveryTelemetryObserver
from osca.security.infrastructure import KeyringVault


@lru_cache(maxsize=1)
def recovery_engine() -> Engine:
    return create_sqlite_engine(_database_path())


def _database_path() -> Path:
    return Path(os.environ.get("OSCA_DATABASE_PATH", "osca.db")).expanduser().resolve()


def _age_executable() -> Path:
    configured = os.environ.get("OSCA_AGE_PATH")
    candidate = configured or shutil.which("age") or "/usr/bin/age"
    return Path(candidate).expanduser().resolve()


def persist_configuration_snapshot(configuration: ValidatedConfiguration) -> None:
    with Session(recovery_engine()) as session, session.begin():
        SqliteConfigurationRepository(session).add(configuration)


@contextmanager
def recovery_service() -> Iterator[RecoveryService]:
    engine = recovery_engine()
    operation_session = Session(engine, expire_on_commit=False)
    catalog_session = Session(engine, expire_on_commit=False)
    audit_session = Session(engine, expire_on_commit=False)
    try:
        yield RecoveryService(
            container=AgeProcessContainer(_age_executable()),
            vault=KeyringVault(),
            catalog=SqliteResultCatalog(catalog_session),
            audit=SqliteAuditRepository(audit_session),
            operations=SqliteRecoveryOperationRepository(operation_session),
            configuration=SqliteConfigurationRepository(catalog_session),
            source_database=_database_path(),
            observer=RecoveryTelemetryObserver(
                telemetry=configure_telemetry(service_version=__version__)
            ),
        )
        catalog_session.commit()
        audit_session.commit()
    except Exception:
        catalog_session.rollback()
        audit_session.commit()
        raise
    finally:
        catalog_session.close()
        audit_session.close()
        operation_session.close()
