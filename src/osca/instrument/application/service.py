from osca.instrument.api import InstrumentReference, MappingVerification, ProviderMapping
from osca.instrument.application.ports import InstrumentRepository


class DuplicateInstrumentError(ValueError):
    pass


class AmbiguousMappingError(ValueError):
    pass


class UnverifiedMappingError(ValueError):
    pass


class InstrumentRegistry:
    def __init__(self, repository: InstrumentRepository) -> None:
        self._repository = repository

    def register(self, instrument: InstrumentReference) -> InstrumentReference:
        if self._repository.find_by_identity(instrument.identity_key) is not None:
            raise DuplicateInstrumentError("canonical instrument identity already exists")
        self._repository.add_instrument(instrument)
        return instrument

    def map_provider(self, mapping: ProviderMapping) -> ProviderMapping:
        if mapping.verification is not MappingVerification.VERIFIED:
            raise UnverifiedMappingError("only verified mappings may become active")
        if self._repository.get_instrument(mapping.instrument_id) is None:
            raise ValueError("canonical instrument does not exist")
        conflicts = tuple(
            existing
            for existing in self._repository.mappings_for_alias(mapping)
            if existing.mapping_id != mapping.mapping_id
            and existing.instrument_id != mapping.instrument_id
            and existing.verification is MappingVerification.VERIFIED
            and existing.overlaps(mapping)
        )
        if conflicts:
            raise AmbiguousMappingError("provider alias overlaps another canonical instrument")
        self._repository.add_mapping(mapping)
        return mapping
