# ADR-0019 — M2 Canonical Daily-Bar Numeric Representation

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Architecture and data authorities
- **Scope:** M2 provider observations, canonical daily-bar contract, Parquet schema, normalization, validation, migration, and export
- **Related requirements:** REQ-0030–REQ-0033, REQ-0038
- **Related product decisions:** D-013, D-017
- **Supersedes:** None
- **Superseded by:** None

## Context

M2 must preserve exact daily OHLCV meaning without binary floating-point ambiguity across provider parsing, canonical normalization, Parquet persistence, validation, export, and recovery. Stocks and crypto pairs require fractional prices, and crypto volume can require substantially more scale than equity volume.

## Decision

The 1.0.0 canonical daily-bar contract and Parquet schema use signed fixed-point `DECIMAL(38,18)` for open, high, low, close, and volume.

Values are finite decimals with at most 38 total digits and at most 18 fractional digits. Parsers must construct decimals from exact textual or integer provider representations, never through a binary float. Excess precision, scale, or range fails validation; it is not rounded silently.

Other temporal and identity fields retain explicit logical types:

- effective date: Parquet `DATE32`;
- source timestamp: timezone-aware UTC microsecond timestamp;
- interval: literal `1d`;
- completion: explicit boolean;
- canonical instrument, provider, request, source, dataset, schema, revision, and integrity identities: typed stable values.

Price currency and volume-unit semantics are required contract metadata. Adjusted bars remain outside M2.

## Consequences

One schema serves stock and crypto fixtures and prevents provider-specific numeric contracts. Decimal128 supports the selected precision in Parquet/PyArrow. Storage is larger than scaled integers or narrower decimals, and arithmetic may be slower, but M2 prioritizes semantic integrity and portability over analytical optimization.

Changing precision or scale is a persisted semantic change requiring compatibility evidence and migration; a change that supported 1.x consumers cannot interpret safely requires a new major contract version.

## Fitness and verification

- exact values round-trip contract → Arrow → Parquet → Arrow → contract;
- maximum supported integral and fractional values round-trip;
- excess scale/range, non-finite values, and float-derived ambiguity are rejected;
- OHLC comparisons operate in decimal space;
- schema fingerprints and canonical digests are deterministic;
- stock and crypto golden fixtures use the identical physical numeric schema;
- no canonical persistence path uses binary floating types.

## Revisit triggers

A supported provider requires legitimate values outside the selected envelope, PyArrow/Parquet cannot preserve the governed semantics on a supported platform, or M3 accepts a new numeric contract with complete migration and compatibility evidence.
