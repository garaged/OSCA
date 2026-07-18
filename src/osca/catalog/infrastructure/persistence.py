from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from osca.catalog.api import (
    CatalogRecoveryReference,
    CatalogResultReference,
    MetadataAvailability,
    RecoveryRecordKind,
    metadata_digest,
)
from osca.shared_kernel.api import CorrelationId


class CatalogBase(DeclarativeBase):
    pass


class CatalogResultRow(CatalogBase):
    __tablename__ = "catalog_result_metadata"
    result_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    producing_run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    media_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class CatalogRecoveryRow(CatalogBase):
    __tablename__ = "catalog_recovery_metadata"
    record_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kind: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    subject_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class SqliteResultCatalog:
    def __init__(self, session: Session) -> None:
        self._session = session

    def register(
        self,
        producing_run_id: UUID,
        correlation_id: CorrelationId,
        producer_build: str,
        media_type: str = "application/json",
    ) -> CatalogResultReference:
        reference = CatalogResultReference(
            producing_run_id=producing_run_id,
            correlation_id=correlation_id,
            producer_build=producer_build,
            lineage=(producing_run_id,),
            media_type=media_type,
        )
        reference = reference.model_copy(
            update={
                "integrity_digest": metadata_digest(
                    reference.model_dump(mode="json", exclude={"integrity_digest"})
                )
            }
        )
        self._session.add(
            CatalogResultRow(
                result_id=str(reference.result_id),
                producing_run_id=str(producing_run_id),
                correlation_id=str(correlation_id.value),
                registered_at=reference.registered_at,
                media_type=media_type,
                payload=reference.model_dump_json(),
            )
        )
        self._session.flush()
        return reference

    def register_recovery(
        self,
        *,
        kind: RecoveryRecordKind,
        subject_id: UUID,
        correlation_id: CorrelationId,
        producer_build: str,
        source_schema: str,
        configuration_revision: UUID,
        lineage: tuple[UUID, ...],
        availability: MetadataAvailability,
    ) -> CatalogRecoveryReference:
        reference = CatalogRecoveryReference(
            kind=kind,
            subject_id=subject_id,
            correlation_id=correlation_id,
            producer_build=producer_build,
            source_schema=source_schema,
            configuration_revision=configuration_revision,
            lineage=lineage,
            availability=availability,
        )
        reference = reference.model_copy(
            update={
                "integrity_digest": metadata_digest(
                    reference.model_dump(mode="json", exclude={"integrity_digest"})
                )
            }
        )
        self._session.add(
            CatalogRecoveryRow(
                record_id=str(reference.record_id),
                kind=reference.kind,
                subject_id=str(reference.subject_id),
                correlation_id=str(correlation_id.value),
                registered_at=reference.registered_at,
                payload=reference.model_dump_json(),
            )
        )
        self._session.flush()
        return reference
