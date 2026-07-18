from uuid import UUID

from sqlalchemy import String, Text, UniqueConstraint, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from osca.instrument.api import InstrumentReference, ProviderMapping


class InstrumentBase(DeclarativeBase):
    pass


class InstrumentRow(InstrumentBase):
    __tablename__ = "instrument_references"
    instrument_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    identity_key: Mapped[str] = mapped_column(String(640), unique=True, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class ProviderMappingRow(InstrumentBase):
    __tablename__ = "instrument_provider_mappings"
    __table_args__ = (
        UniqueConstraint("provider_id", "provider_symbol", "scope", "venue_context", "valid_from"),
    )
    mapping_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    instrument_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    provider_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    provider_symbol: Mapped[str] = mapped_column(String(128), nullable=False)
    scope: Mapped[str] = mapped_column(String(128), nullable=False)
    venue_context: Mapped[str] = mapped_column(String(128), nullable=False)
    valid_from: Mapped[str] = mapped_column(String(10), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


def _identity_key(value: tuple[str, ...]) -> str:
    return "\x1f".join(value)


class SqliteInstrumentRepository:
    """Instrument-owned adapter; other capabilities consume the public application port."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add_instrument(self, instrument: InstrumentReference) -> None:
        self._session.add(
            InstrumentRow(
                instrument_id=str(instrument.instrument_id),
                identity_key=_identity_key(instrument.identity_key),
                payload=instrument.model_dump_json(),
            )
        )
        self._session.flush()

    def get_instrument(self, instrument_id: UUID) -> InstrumentReference | None:
        row = self._session.get(InstrumentRow, str(instrument_id))
        return None if row is None else InstrumentReference.model_validate_json(row.payload)

    def find_by_identity(self, identity_key: tuple[str, ...]) -> InstrumentReference | None:
        row = self._session.scalar(
            select(InstrumentRow).where(InstrumentRow.identity_key == _identity_key(identity_key))
        )
        return None if row is None else InstrumentReference.model_validate_json(row.payload)

    def add_mapping(self, mapping: ProviderMapping) -> None:
        self._session.add(
            ProviderMappingRow(
                mapping_id=str(mapping.mapping_id),
                instrument_id=str(mapping.instrument_id),
                provider_id=mapping.provider_id,
                provider_symbol=mapping.provider_symbol,
                scope=mapping.scope,
                venue_context=mapping.venue_context,
                valid_from=mapping.valid_from.isoformat(),
                payload=mapping.model_dump_json(),
            )
        )
        self._session.flush()

    def mappings_for_alias(self, mapping: ProviderMapping) -> tuple[ProviderMapping, ...]:
        rows = self._session.scalars(
            select(ProviderMappingRow).where(
                ProviderMappingRow.provider_id == mapping.provider_id,
                ProviderMappingRow.provider_symbol == mapping.provider_symbol,
                ProviderMappingRow.scope == mapping.scope,
                ProviderMappingRow.venue_context == mapping.venue_context,
            )
        ).all()
        return tuple(ProviderMapping.model_validate_json(row.payload) for row in rows)
