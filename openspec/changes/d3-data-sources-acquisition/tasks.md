# Tasks: D3 Data Sources, Credentials, Import, and Acquisition UX

## Specification and governance

- [x] Convert D3 intent into an executable specification.
- [x] Allocate REQ-0294 through REQ-0308.
- [x] Add D3 OpenSpec proposal and delta specification.
- [x] Add initial D3 traceability and implementation disposition.
- [x] Add supported-platform clean-profile manual acceptance procedure.
- [x] Update implementation traceability and focused validation coverage.
- [ ] Update final capability map, product/development/user documentation, and validation evidence after acceptance.
- [ ] Complete D3 exit review.

## Provider catalog and capability resolution

- [x] Add typed provider catalog and capability-status desktop contracts.
- [x] Derive provider rows from canonical admission policy.
- [x] Keep admission, credential, network, profile, and resource states separate.
- [x] Show approved resources, credential mode, evidence date, rationale, findings, and promotion blockers.
- [x] Preserve free/offline sample and local import paths.

## Secure credentials

- [x] Add credential reference mapping for named-secret providers.
- [x] Compose production desktop service with `KeyringVault`.
- [x] Add store/replace, probe, and delete application methods.
- [x] Map vault missing/denied/unavailable outcomes to safe typed responses.
- [x] Prove secret values never return through the desktop protocol or persist in frontend state/evidence.
- [x] Keep credential presence from changing admission or approved resources.

## Local import

- [x] Add typed local OHLCV import request and result desktop methods.
- [x] Delegate validation and persistence to canonical local import.
- [x] Add source, calendar, symbol, timeframe, lineage, and idempotency display.
- [x] Add malformed/unsafe-path and failure-atomic tests.

## Kraken acquisition and jobs

- [x] Add typed Kraken request validation and explicit request-scoped network consent.
- [x] Delegate acquisition to canonical historical-acquisition service.
- [x] Add retained job/evidence inspection.
- [x] Preserve canonical pre-network cancellation, retry/reuse, and interrupted-job recovery behavior.
- [x] Preserve policy/quota/provider/partial/stale/invalid/corrupt/cancelled/failed distinctions.
- [x] Prove no-key Kraken acquisition and internal-use-only/redistribution-disabled status.

## React and Rust desktop

- [x] Add Data Sources application destination and responsive accessible surfaces.
- [x] Add provider, credential, import, acquisition, evidence, warning, and destructive-action states.
- [x] Add strict TypeScript response validation.
- [x] Preserve keyboard/focus/reduced-motion/forced-colors behavior in implementation.
- [x] Preserve the single narrow `desktop_request` command and restrictive CSP.
- [x] Add architecture tests preventing generic keychain, HTTP, file, shell, SQLite, or Parquet authority.

## Validation and evidence

- [x] Add Python provider-policy, vault, redaction, import, acquisition, cancellation, retry, and recovery tests.
- [x] Add frontend state/source/architecture tests.
- [ ] Pass final draft-head Ruff, strict mypy, complete pytest, OpenSpec, secret scan, TypeScript, and Rust checks.
- [ ] Run ready-state Linux x86-64 and macOS ARM64 contributor/package lifecycle validation and Linux package smoke.
- [ ] Execute macOS ARM64 manual acceptance.
- [ ] Execute Linux x86-64 manual acceptance.
- [ ] Resolve all security, accessibility, data-integrity, and network-consent defects.
- [ ] Retain final D3 validation evidence and explicit owner acceptance.
