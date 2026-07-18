from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

Identifier = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")]
CurrencyCode = Annotated[str, Field(min_length=3, max_length=12, pattern=r"^[A-Z0-9]+$")]


class AssetClass(StrEnum):
    STOCK = "stock"
    CRYPTO_PAIR = "crypto_pair"


class InstrumentLifecycle(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELISTED = "delisted"


class MappingVerification(StrEnum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    QUARANTINED = "quarantined"


class InstrumentReference(BaseModel):
    """Provider-neutral canonical instrument identity (osca.instrument.reference 1.0.0)."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)
    family: Literal["osca.instrument.reference"] = "osca.instrument.reference"
    version: Literal["1.0.0"] = "1.0.0"
    instrument_id: UUID = Field(default_factory=uuid4)
    asset_class: AssetClass
    listing_venue: Identifier
    currency: CurrencyCode
    lifecycle: InstrumentLifecycle = InstrumentLifecycle.ACTIVE
    display_symbol: Identifier
    external_identity: Identifier | None = None
    base_asset: Identifier | None = None
    quote_asset: Identifier | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_asset_identity(self) -> Self:
        pair_fields = (self.base_asset, self.quote_asset)
        if self.asset_class is AssetClass.CRYPTO_PAIR and any(v is None for v in pair_fields):
            raise ValueError("crypto_pair requires base_asset and quote_asset")
        if self.asset_class is AssetClass.STOCK and any(v is not None for v in pair_fields):
            raise ValueError("stock cannot declare base_asset or quote_asset")
        if self.base_asset is not None and self.base_asset == self.quote_asset:
            raise ValueError("base_asset and quote_asset must differ")
        return self

    @property
    def identity_key(self) -> tuple[str, ...]:
        if self.asset_class is AssetClass.STOCK:
            stable = self.external_identity or self.display_symbol
            return (self.asset_class, self.listing_venue, self.currency, stable)
        return (
            self.asset_class,
            self.listing_venue,
            self.currency,
            self.base_asset or "",
            self.quote_asset or "",
        )


class ProviderMapping(BaseModel):
    """Time-aware provider alias; never a canonical primary identity."""

    model_config = ConfigDict(frozen=True, str_strip_whitespace=True)
    family: Literal["osca.instrument.provider-mapping"] = "osca.instrument.provider-mapping"
    version: Literal["1.0.0"] = "1.0.0"
    mapping_id: UUID = Field(default_factory=uuid4)
    instrument_id: UUID
    provider_id: Identifier
    provider_symbol: Identifier
    scope: Identifier
    venue_context: Identifier
    valid_from: date
    valid_to: date | None = None
    provenance: Annotated[str, Field(min_length=1, max_length=512)]
    verification: MappingVerification = MappingVerification.UNVERIFIED
    capabilities: frozenset[Identifier] = Field(min_length=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_validity(self) -> Self:
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("valid_to must be on or after valid_from")
        return self

    def overlaps(self, other: "ProviderMapping") -> bool:
        if (self.provider_id, self.provider_symbol, self.scope, self.venue_context) != (
            other.provider_id,
            other.provider_symbol,
            other.scope,
            other.venue_context,
        ):
            return False
        return (self.valid_to is None or other.valid_from <= self.valid_to) and (
            other.valid_to is None or self.valid_from <= other.valid_to
        )
