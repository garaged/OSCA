from uuid import UUID

from sqlalchemy import Integer, String, Text, UniqueConstraint, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from osca.market_data.api import DatasetManifest, ManifestState


class MarketDataBase(DeclarativeBase):
    pass


class DatasetManifestRow(MarketDataBase):
    __tablename__ = "market_data_dataset_manifests"
    __table_args__ = (UniqueConstraint("fingerprint", name="uq_market_data_fingerprint"),)
    manifest_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    dataset_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)
    fingerprint: Mapped[str] = mapped_column(String(71), nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    instrument_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class SqliteManifestRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, manifest: DatasetManifest) -> None:
        self._session.add(
            DatasetManifestRow(
                manifest_id=str(manifest.manifest_id),
                dataset_id=str(manifest.dataset_id),
                revision=manifest.revision,
                fingerprint=manifest.fingerprint,
                state=manifest.state,
                instrument_id=str(manifest.instrument_id),
                payload=manifest.model_dump_json(),
            )
        )
        self._session.flush()

    def by_fingerprint(self, fingerprint: str) -> DatasetManifest | None:
        row = self._session.scalar(
            select(DatasetManifestRow).where(DatasetManifestRow.fingerprint == fingerprint)
        )
        return None if row is None else DatasetManifest.model_validate_json(row.payload)

    def transition(
        self,
        manifest_id: UUID,
        *,
        expected: ManifestState,
        target: ManifestState,
    ) -> DatasetManifest:
        allowed = {
            (ManifestState.STAGING, ManifestState.READY),
            (ManifestState.STAGING, ManifestState.QUARANTINED),
            (ManifestState.READY, ManifestState.DELETING),
            (ManifestState.QUARANTINED, ManifestState.DELETING),
            (ManifestState.DELETING, ManifestState.DELETED),
        }
        if (expected, target) not in allowed:
            raise ValueError("manifest state transition is not allowed")
        row = self._session.get(DatasetManifestRow, str(manifest_id))
        if row is None:
            raise LookupError("manifest does not exist")
        manifest = DatasetManifest.model_validate_json(row.payload)
        if manifest.state is not expected:
            raise ValueError("manifest state changed before transition")
        transitioned = manifest.model_copy(update={"state": target})
        row.state = target
        row.payload = transitioned.model_dump_json()
        self._session.flush()
        return transitioned

    def ready(self, dataset_id: UUID) -> tuple[DatasetManifest, ...]:
        rows = self._session.scalars(
            select(DatasetManifestRow)
            .where(
                DatasetManifestRow.dataset_id == str(dataset_id),
                DatasetManifestRow.state == ManifestState.READY,
            )
            .order_by(DatasetManifestRow.revision)
        ).all()
        return tuple(DatasetManifest.model_validate_json(row.payload) for row in rows)
