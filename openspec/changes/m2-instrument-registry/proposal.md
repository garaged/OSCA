# M2.1 Instrument Registry

## Intent

Implement the smallest governed Instrument capability slice: provider-neutral stock and spot-crypto-pair registration plus time-aware verified provider mappings.

## Authority

REQ-0021–REQ-0024; D-012; ADR-0003, ADR-0004, ADR-0005, ADR-0009, ADR-0012, ADR-0017; accepted M2 intent and specification; RISK-M2-001.

## Scope

- accept exact instrument-reference and provider-mapping 1.0.0 contracts;
- add capability-owned SQLite schemas and migration;
- reject duplicate canonical identity and unverified or ambiguous mappings;
- retain deterministic component and migration evidence.

Market-data retrieval, provider networking, daily bars, payload persistence, and production provider selection are excluded.
