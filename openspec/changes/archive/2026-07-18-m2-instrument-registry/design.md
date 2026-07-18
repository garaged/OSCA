# Design

Instrument owns canonical identities, provider aliases, repositories, and migrations. Public immutable Pydantic contracts live under `osca.instrument.api`; application ports and services depend only on those contracts; SQLite infrastructure implements the owned repository.

Stock identity distinguishes listing venue, currency, and stable external identity where available. Crypto-pair identity distinguishes venue/scope, currency, base asset, and quote asset. Display and provider symbols never form provider-controlled primary identity.

Mappings include canonical identity, provider, symbol, scope, venue context, validity, provenance, verification, and capabilities. Only verified mappings for an existing instrument may activate. Overlapping verified aliases bound to different instruments fail before downstream canonical writes.
