# D3 Traceability — Data Sources, Credentials, Import, and Acquisition UX

- **Status:** Implementation complete; ready-state and supported-platform acceptance pending
- **Governing intent:** `docs/milestones/d3/intent.md`
- **Specification:** `docs/milestones/d3/specification.md`
- **Requirements:** `docs/governance/requirements-catalog-d3.md`
- **OpenSpec:** `openspec/changes/d3-data-sources-acquisition/`

## Requirement mapping

| Requirement | Implemented behavior | Canonical implementation authority | Verification | Status |
|---|---|---|---|---|
| REQ-0294 | Policy-derived provider catalog | `desktop_api.data_sources`; `production_ingestion.policy` | D3 catalog tests | Implemented |
| REQ-0295 | Admission, credential, network, profile, resource, and operational states remain separate | D3 catalog and frontend typed models | Policy-negative and frontend tests | Implemented |
| REQ-0296 | Sample/local import remain free and offline; Kraken remains no-key | Existing sample/import services; D3 acquisition service | Integration tests | Implemented |
| REQ-0297 | Secrets use `SecretVault`/`KeyringVault` and never return to React | D3 desktop service and security ports | Redaction and architecture tests | Implemented |
| REQ-0298 | Store/replace, probe, and delete named credentials | `desktop_api.data_sources` | Unit and desktop API tests | Implemented |
| REQ-0299 | Only admitted resources run acquisition | `admission_for`; canonical acquisition service | Policy integration tests | Implemented |
| REQ-0300 | Network consent is explicit per acquisition request | D3 acquisition request; React consent control | Network-negative and source tests | Implemented |
| REQ-0301 | Governed CSV import delegates to canonical import | D3 service; `local_data_import` | Validation, lineage, and atomicity tests | Implemented |
| REQ-0302 | Kraken public OHLC delegates to canonical acquisition | D3 acquisition service; `historical_acquisition` | Deterministic transport tests | Implemented |
| REQ-0303 | Typed acquisition and retained-evidence results | Historical evidence records; D3 evidence list | Contract tests | Implemented |
| REQ-0304 | Pre-network cancellation, reuse, and interrupted-job recovery remain canonical | `historical_acquisition` | Cancellation/reuse/recovery tests | Implemented |
| REQ-0305 | Blocked and failure outcomes remain distinct | Historical status enums and typed desktop responses | Contract tests | Implemented |
| REQ-0306 | React uses only `desktop_request`; Rust gains no generic authority | D2 Rust broker; D3 typed clients | Frontend architecture tests | Implemented |
| REQ-0307 | Responsive Data Sources UI with keyboard, focus, reduced-motion, and forced-colors safeguards | `DataSources.tsx`; D3 composition CSS | Build/source tests; manual acceptance pending | Implemented; manual pending |
| REQ-0308 | Evidence-based milestone exit | D3 docs, CI, acceptance evidence, exit review | Traceability audit | In progress |

## Implemented files

- `src/osca/desktop_api/data_sources.py`
- `src/osca/desktop_api/d3_service.py`
- `src/osca/desktop_api/d3_acquisition_service.py`
- `src/osca/desktop_api/stdio.py`
- `apps/desktop/src/dataSourcesApi.ts`
- `apps/desktop/src/DataSources.tsx`
- `apps/desktop/src/dataSources.css`
- `apps/desktop/src/D3Root.tsx`
- `apps/desktop/src/d3Root.css`
- focused Python and frontend D3 test suites

## Retained boundaries and limitations

- The sidecar remains short-lived and request/response based.
- Acquisition is therefore presented as synchronous; no fake live progress or active cross-request cancellation is claimed.
- Pre-network cancellation, deterministic reuse, recovery, retained evidence, and typed completion/failure outcomes remain available.
- No paid provider is required.
- No credential promotes provider admission.
- No recommendation, broker, exchange, autonomous, live-order, or real-capital path exists.

## Remaining exit blockers

- Confirm the final draft-head Quality and Desktop Foundation checks.
- Mark the PR ready only after explicit owner direction.
- Pass non-draft Linux/macOS contributor and package-lifecycle matrices plus Linux package smoke.
- Pass macOS ARM64 and Linux x86-64 clean-profile manual acceptance.
- Resolve any security, accessibility, data-integrity, or network-consent defects.
- Retain final validation evidence and D3 exit review.
- Obtain explicit owner direction before merge.
