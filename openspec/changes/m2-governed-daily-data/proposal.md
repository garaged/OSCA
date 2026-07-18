## Why

M2.1 and M2.2 established canonical instrument identity and provider-neutral acquisition contracts. The remaining M2.3–M2.9 work must deliver governed daily ingestion, durable resolution and repair, quality, inspection, conditional reference adapters, documentation, and exit evidence under REQ-0030–REQ-0040.

## What Changes

- Add accepted Market Data contracts and immutable SQLite manifest metadata.
- Normalize exact daily OHLCV observations into protected canonical revisions.
- Resolve freshness, completeness, exact pins, gaps, and safe repair ranges explicitly.
- Produce deterministic quality findings and cleanup previews that protect canonical history.
- Add Twelve Data and Kraken parsers behind injected, policy-governed I/O; keep production visibility blocked until provider-specific promotion evidence is accepted.
- Complete migrations, operations, documentation, traceability, and retained M2 evidence.

## Capabilities

### New Capabilities

- `m2-governed-daily-data`: Governed daily ingestion, retrieval, repair, quality, inspection, and cleanup behavior.

### Modified Capabilities

- `provider-daily-acquisition`: Adds conditional candidate parsers without changing the accepted provider-neutral contract.

## Impact

- **Owning capability:** Market Data owns daily contracts, normalization, manifests, revisions, retrieval, findings, and cleanup plans.
- **Affected contracts:** `osca.market-data.daily-bar`, `osca.market-data.dataset-manifest`, `osca.market-data.retrieval-request`, `osca.market-data.resolution`, `osca.data-quality.finding`, and `osca.cache.cleanup-plan` 1.0.0.
- **Supporting capabilities:** Instrument supplies canonical identity/mappings; Provider supplies observations/policy; Workflow supplies durable work; Catalog receives public metadata; Operations owns telemetry/audit.
- **Governing architecture:** ADR-0003–ADR-0007, ADR-0009, ADR-0010, ADR-0012–ADR-0015, and ADR-0017–ADR-0026.
- **Risk class:** Governed high-risk data-integrity, licensing, persistence, and external-adapter change.
- **Non-goals:** intraday data, adjusted bars, corporate actions, complete exchange calendars, cross-provider merging, automated reclamation, and provider production promotion without accepted evidence.
