# P4 No-Cost Provider Adapter Contracts Specification

## Purpose

P4 defines deterministic adapter contracts for the preferred no-cost provider profiles selected by P3: SEC EDGAR and FRED.

## Requirements

- REQ-0184: Adapter contracts must be limited to preferred no-cost providers.
- REQ-0185: SEC EDGAR contracts must preserve public no-key access, user-agent, and fair-access constraints.
- REQ-0186: FRED contracts must preserve named API-key reference requirements without credential values.
- REQ-0187: Adapter requests must preserve provider, endpoint, resource identity, parameters, and disabled network access.
- REQ-0188: Fixture validation must preserve provider, endpoint, checksum, source URI, record count, and disabled network access.
- REQ-0189: P4 must not enable live provider calls, runtime routing, production promotion, or production ingestion.
- REQ-0190: P4 completion requires retained code, tests, documentation, traceability, ADR, OpenSpec, and hosted Quality evidence.

## Deferred boundary

P4 is an adapter-contract milestone. It is not a provider runtime milestone.
