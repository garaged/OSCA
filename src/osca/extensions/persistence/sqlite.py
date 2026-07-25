import sqlite3
from pathlib import Path
from typing import cast
from uuid import UUID

from osca.extensions.api import (
    ExtensionActivationDecision,
    ExtensionInstallationRecord,
)

_SCHEMA_VERSION = 1


class SQLiteExtensionLifecycleStore:
    """SQLite store for extension installation and activation lifecycle records."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = str(database_path)

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS extension_store_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS extension_installations (
                    installation_id TEXT PRIMARY KEY,
                    package_id TEXT NOT NULL,
                    package_version TEXT NOT NULL,
                    activation_state TEXT NOT NULL,
                    installed_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_extension_installations_package
                    ON extension_installations(package_id, package_version);

                CREATE TABLE IF NOT EXISTS extension_activation_decisions (
                    decision_id TEXT PRIMARY KEY,
                    installation_id TEXT NOT NULL,
                    approved INTEGER NOT NULL,
                    decided_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    FOREIGN KEY (installation_id)
                        REFERENCES extension_installations(installation_id)
                        ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS idx_extension_activation_installation
                    ON extension_activation_decisions(installation_id, decided_at);
                """
            )
            connection.execute(
                """
                INSERT INTO extension_store_metadata(key, value)
                VALUES ('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(_SCHEMA_VERSION),),
            )

    def save_installation(self, record: ExtensionInstallationRecord) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO extension_installations(
                    installation_id,
                    package_id,
                    package_version,
                    activation_state,
                    installed_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(installation_id) DO UPDATE SET
                    package_id = excluded.package_id,
                    package_version = excluded.package_version,
                    activation_state = excluded.activation_state,
                    installed_at = excluded.installed_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(record.installation_id),
                    record.package_id,
                    record.package_version,
                    record.activation_state.value,
                    record.installed_at.isoformat(),
                    record.model_dump_json(),
                ),
            )

    def get_installation(self, installation_id: UUID) -> ExtensionInstallationRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json
                FROM extension_installations
                WHERE installation_id = ?
                """,
                (str(installation_id),),
            ).fetchone()
        if row is None:
            return None
        return ExtensionInstallationRecord.model_validate_json(cast(str, row["payload_json"]))

    def list_installations(
        self, *, package_id: str | None = None
    ) -> tuple[ExtensionInstallationRecord, ...]:
        query = "SELECT payload_json FROM extension_installations"
        parameters: tuple[str, ...] = ()
        if package_id is not None:
            query += " WHERE package_id = ?"
            parameters = (package_id,)
        query += " ORDER BY installed_at, installation_id"

        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return tuple(
            ExtensionInstallationRecord.model_validate_json(cast(str, row["payload_json"]))
            for row in rows
        )

    def save_activation_decision(self, decision: ExtensionActivationDecision) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO extension_activation_decisions(
                    decision_id,
                    installation_id,
                    approved,
                    decided_at,
                    payload_json
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(decision_id) DO UPDATE SET
                    installation_id = excluded.installation_id,
                    approved = excluded.approved,
                    decided_at = excluded.decided_at,
                    payload_json = excluded.payload_json
                """,
                (
                    str(decision.decision_id),
                    str(decision.installation_id),
                    int(decision.approved),
                    decision.decided_at.isoformat(),
                    decision.model_dump_json(),
                ),
            )

    def get_activation_decision(self, decision_id: UUID) -> ExtensionActivationDecision | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload_json
                FROM extension_activation_decisions
                WHERE decision_id = ?
                """,
                (str(decision_id),),
            ).fetchone()
        if row is None:
            return None
        return ExtensionActivationDecision.model_validate_json(cast(str, row["payload_json"]))

    def list_activation_decisions(
        self, *, installation_id: UUID | None = None
    ) -> tuple[ExtensionActivationDecision, ...]:
        query = "SELECT payload_json FROM extension_activation_decisions"
        parameters: tuple[str, ...] = ()
        if installation_id is not None:
            query += " WHERE installation_id = ?"
            parameters = (str(installation_id),)
        query += " ORDER BY decided_at, decision_id"

        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return tuple(
            ExtensionActivationDecision.model_validate_json(cast(str, row["payload_json"]))
            for row in rows
        )

    def list_activation_decisions_for_package(
        self, package_id: str
    ) -> tuple[ExtensionActivationDecision, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT decision.payload_json
                FROM extension_activation_decisions AS decision
                JOIN extension_installations AS installation
                    ON installation.installation_id = decision.installation_id
                WHERE installation.package_id = ?
                ORDER BY decision.decided_at, decision.decision_id
                """,
                (package_id,),
            ).fetchall()
        return tuple(
            ExtensionActivationDecision.model_validate_json(cast(str, row["payload_json"]))
            for row in rows
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection
