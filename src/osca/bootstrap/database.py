from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

_BUSY_TIMEOUT_MILLISECONDS = 5_000


def create_sqlite_engine(database_path: Path) -> Engine:
    """Create the governed M1 metadata engine with safe SQLite defaults."""

    resolved = database_path.expanduser().resolve()
    resolved.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{resolved}", future=True)

    @event.listens_for(engine, "connect")
    def configure_connection(dbapi_connection: object, _record: object) -> None:
        cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute(f"PRAGMA busy_timeout={_BUSY_TIMEOUT_MILLISECONDS}")
            cursor.execute("PRAGMA journal_mode=WAL")
        finally:
            cursor.close()

    return engine


def check_sqlite_integrity(engine: Engine) -> bool:
    with engine.connect() as connection:
        result = connection.execute(text("PRAGMA integrity_check")).scalar_one()
    return str(result) == "ok"


class SessionProvider:
    def __init__(self, engine: Engine) -> None:
        self._factory = sessionmaker(bind=engine, expire_on_commit=False)

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        session = self._factory()
        try:
            with session.begin():
                yield session
        finally:
            session.close()
