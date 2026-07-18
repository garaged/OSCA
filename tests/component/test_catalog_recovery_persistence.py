from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.catalog.api import MetadataAvailability, RecoveryRecordKind
from osca.catalog.infrastructure import CatalogBase, SqliteResultCatalog
from osca.shared_kernel.api import CorrelationId


def test_catalog_recovery_metadata_round_trip() -> None:
    engine = create_engine("sqlite://")
    CatalogBase.metadata.create_all(engine)
    subject_id = uuid4()
    configuration_revision = uuid4()
    with Session(engine) as session, session.begin():
        reference = SqliteResultCatalog(session).register_recovery(
            kind=RecoveryRecordKind.BACKUP,
            subject_id=subject_id,
            correlation_id=CorrelationId.new(),
            producer_build="test-build",
            source_schema="m1_0005",
            configuration_revision=configuration_revision,
            lineage=(configuration_revision,),
            availability=MetadataAvailability.AVAILABLE,
        )
        assert reference.subject_id == subject_id
        assert reference.verify_integrity()
