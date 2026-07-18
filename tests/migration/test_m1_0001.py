from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def _config(database_path: Path) -> Config:
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")
    return config


def test_initial_migration_upgrades_and_downgrades_clean_database(tmp_path: Path) -> None:
    database_path = tmp_path / "migrated.db"
    config = _config(database_path)

    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database_path}")
    assert inspect(engine).get_table_names() == [
        "alembic_version",
        "catalog_recovery_metadata",
        "catalog_result_metadata",
        "configuration_snapshots",
        "instrument_provider_mappings",
        "instrument_references",
        "operations_audit_records",
        "operations_workflow_events",
        "recovery_operations",
        "workflow_diagnostic_runs",
    ]

    command.downgrade(config, "base")
    assert inspect(engine).get_table_names() == ["alembic_version"]
