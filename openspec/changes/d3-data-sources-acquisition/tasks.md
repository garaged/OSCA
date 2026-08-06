# Tasks: D3 Data Sources, Credentials, Import, and Acquisition UX

## Specification and governance

- [x] Convert D3 intent into an executable specification.
- [x] Allocate REQ-0294 through REQ-0308.
- [x] Add D3 OpenSpec proposal and delta specification.
- [x] Add initial D3 traceability and implementation disposition.
- [x] Add supported-platform clean-profile manual acceptance procedure.
- [ ] Update capability map, product traceability, development/user documentation, and validation evidence.
- [ ] Complete D3 exit review.

## Provider catalog and capability resolution

- [ ] Add typed provider catalog and capability-status desktop contracts.
- [ ] Derive provider rows from canonical admission policy.
- [ ] Keep admission, credential, network, profile, and resource states separate.
- [ ] Show approved resources, credential mode, evidence date, rationale, findings, and promotion blockers.
- [ ] Preserve free/offline sample and local import paths.

## Secure credentials

- [ ] Add credential reference mapping for named-secret providers.
- [ ] Compose production desktop service with `KeyringVault`.
- [ ] Add store/replace, probe, and delete application methods.
- [ ] Map vault missing/denied/unavailable outcomes to safe typed responses.
- [ ] Prove secret values never return or persist in state, profile files, databases, logs, URLs, or evidence.
- [ ] Keep credential presence from changing admission or approved resources.

## Local import

- [ ] Add typed local OHLCV import request and result desktop methods.
- [ ] Delegate validation and persistence to canonical local import.
- [ ] Add source, calendar, symbol, timeframe, lineage, and idempotency display.
- [ ] Add malformed/unsafe-path and failure-atomic tests.

## Kraken acquisition and jobs

- [ ] Add typed Kraken request validation and explicit request-scoped network consent.
- [ ] Delegate acquisition to canonical historical-acquisition service.
- [ ] Add retained job/evidence inspection.
- [ ] Add cancellation, retry/reuse, and interrupted-job recovery behavior.
- [ ] Preserve policy/quota/provider/partial/stale/invalid/corrupt/cancelled/failed distinctions.
- [ ] Prove no-key Kraken acquisition and internal-use-only/redistribution-disabled status.

## React and Rust desktop

- [ ] Add Data Sources destination and responsive accessible surfaces.
- [ ] Add provider, credential, import, acquisition, progress, evidence, warning, and confirmation states.
- [ ] Add strict TypeScript response validation.
- [ ] Preserve keyboard/focus/screen-reader/reduced-motion/light-dark/forced-colors behavior.
- [ ] Preserve the single narrow `desktop_request` command and restrictive CSP.
- [ ] Add architecture tests preventing generic keychain, HTTP, file, shell, SQLite, or Parquet authority.

## Validation and evidence

- [ ] Add Python provider-policy, vault, redaction, import, acquisition, job, cancellation, retry, and recovery tests.
- [ ] Add frontend state/render/architecture tests.
- [ ] Pass Ruff, strict mypy, complete pytest, OpenSpec, secret scan, TypeScript, Rust format/unit/Clippy, and package smoke.
- [ ] Run Linux x86-64 and macOS ARM64 contributor/package lifecycle validation.
- [ ] Execute macOS ARM64 manual acceptance.
- [ ] Execute Linux x86-64 manual acceptance.
- [ ] Resolve all security, accessibility, data-integrity, and network-consent defects.
- [ ] Retain final D3 validation evidence and explicit owner acceptance.
