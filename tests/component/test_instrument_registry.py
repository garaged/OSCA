from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from osca.instrument.api import (
    AssetClass,
    InstrumentReference,
    MappingVerification,
    ProviderMapping,
)
from osca.instrument.application import (
    AmbiguousMappingError,
    DuplicateInstrumentError,
    InstrumentRegistry,
    UnverifiedMappingError,
)
from osca.instrument.infrastructure import InstrumentBase, SqliteInstrumentRepository


def stock(symbol: str = "ACME") -> InstrumentReference:
    return InstrumentReference(
        asset_class=AssetClass.STOCK,
        listing_venue="XNYS",
        currency="USD",
        display_symbol=symbol,
        external_identity=f"US-{symbol}",
    )


def mapping(
    instrument: InstrumentReference,
    verification: MappingVerification = MappingVerification.VERIFIED,
) -> ProviderMapping:
    return ProviderMapping(
        instrument_id=instrument.instrument_id,
        provider_id="fixture-stock",
        provider_symbol="ACME",
        scope="daily",
        venue_context="XNYS",
        valid_from=date(2020, 1, 1),
        provenance="reviewed fixture",
        verification=verification,
        capabilities=frozenset({"daily_ohlcv"}),
    )


def test_registers_stock_and_crypto_pair_and_rejects_duplicate_identity() -> None:
    engine = create_engine("sqlite://")
    InstrumentBase.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        registry = InstrumentRegistry(SqliteInstrumentRepository(session))
        equity = registry.register(stock())
        pair = registry.register(
            InstrumentReference(
                asset_class=AssetClass.CRYPTO_PAIR,
                listing_venue="KRAKEN",
                currency="USD",
                display_symbol="BTCUSD",
                base_asset="BTC",
                quote_asset="USD",
            )
        )
        assert equity.instrument_id != pair.instrument_id
        with pytest.raises(DuplicateInstrumentError):
            registry.register(stock("OTHER").model_copy(update={"external_identity": "US-ACME"}))


def test_mapping_must_be_verified_and_unambiguous() -> None:
    engine = create_engine("sqlite://")
    InstrumentBase.metadata.create_all(engine)
    with Session(engine) as session, session.begin():
        registry = InstrumentRegistry(SqliteInstrumentRepository(session))
        first = registry.register(stock())
        second = registry.register(stock("OTHER"))
        with pytest.raises(UnverifiedMappingError):
            registry.map_provider(mapping(first, MappingVerification.UNVERIFIED))
        registry.map_provider(mapping(first))
        with pytest.raises(AmbiguousMappingError):
            registry.map_provider(mapping(second))
