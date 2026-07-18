from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from osca.bootstrap.database import SessionProvider, check_sqlite_integrity, create_sqlite_engine
from osca.configuration.api.contracts import RawConfiguration
from osca.configuration.application import validate_configuration
from osca.configuration.infrastructure import ConfigurationBase, SqliteConfigurationRepository


def test_sqlite_governance_and_configuration_round_trip(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "state" / "osca.db")
    ConfigurationBase.metadata.create_all(engine)
    provider = SessionProvider(engine)
    configuration = validate_configuration(RawConfiguration())

    with provider.transaction() as session:
        SqliteConfigurationRepository(session).add(configuration)

    with provider.transaction() as session:
        restored = SqliteConfigurationRepository(session).get(configuration.revision_id)

    assert restored == configuration
    assert check_sqlite_integrity(engine)
    with engine.connect() as connection:
        assert connection.execute(text("PRAGMA journal_mode")).scalar_one() == "wal"
        assert connection.execute(text("PRAGMA foreign_keys")).scalar_one() == 1
        assert connection.execute(text("PRAGMA busy_timeout")).scalar_one() == 5_000


def test_immutable_revision_cannot_be_overwritten(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "osca.db")
    ConfigurationBase.metadata.create_all(engine)
    provider = SessionProvider(engine)
    configuration = validate_configuration(RawConfiguration())

    with provider.transaction() as session:
        SqliteConfigurationRepository(session).add(configuration)

    with pytest.raises(IntegrityError), provider.transaction() as session:
        SqliteConfigurationRepository(session).add(configuration)


def test_configuration_capability_owns_only_prefixed_tables(tmp_path: Path) -> None:
    engine = create_sqlite_engine(tmp_path / "osca.db")
    ConfigurationBase.metadata.create_all(engine)
    assert inspect(engine).get_table_names() == ["configuration_snapshots"]

