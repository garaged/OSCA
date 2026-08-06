# D3 Traceability — Data Sources, Credentials, Import, and Acquisition UX

- **Status:** Specification complete; implementation pending
- **Governing intent:** `docs/milestones/d3/intent.md`
- **Specification:** `docs/milestones/d3/specification.md`
- **Requirements:** `docs/governance/requirements-catalog-d3.md`
- **OpenSpec:** `openspec/changes/d3-data-sources-acquisition/`

## Requirement mapping

| Requirement | Planned behavior | Canonical implementation authority | Planned verification | Status |
|---|---|---|---|---|
| REQ-0294 | Provider catalog reflects admission policy | `production_ingestion.policy`; desktop API | Contract/component tests | Planned |
| REQ-0295 | Admission, credential, network, profile, and operational states remain separate | Desktop capability resolver | Policy-negative tests | Planned |
| REQ-0296 | Sample/local import stay free and offline; Kraken stays no-key | Existing sample/local import/Kraken services | Integration/manual tests | Planned |
| REQ-0297 | Secrets use OS vault and never return/persist elsewhere | `SecretVault`; `KeyringVault` | Redaction/architecture tests | Planned |
| REQ-0298 | Store/probe/delete named credentials | Security application service and desktop API | Unit/manual tests | Planned |
| REQ-0299 | Only approved resources run | `admission_for` | Policy/integration tests | Planned |
| REQ-0300 | Network consent is explicit per request | Desktop acquisition request and canonical ingestion | Network-negative tests | Planned |
| REQ-0301 | Canonical governed CSV import | `local_data_import` | Validation/lineage tests | Planned |
| REQ-0302 | Canonical Kraken public acquisition | `historical_acquisition` | Fake-transport integration tests | Planned |
| REQ-0303 | Typed job/evidence inspection | Historical evidence and job records | Contract/component tests | Planned |
| REQ-0304 | Cancellation, retry, reuse, and recovery | Historical acquisition job lifecycle | Recovery/concurrency tests | Planned |
| REQ-0305 | Distinct blocked/failure outcomes | Existing enums plus typed desktop response | Contract/component tests | Planned |
| REQ-0306 | Narrow frontend/Rust boundary | `desktop_request`; Python methods | Architecture tests | Planned |
| REQ-0307 | Accessible responsive UX | React D3 surfaces and D2 design system | Component/manual tests | Planned |
| REQ-0308 | Evidence-based exit | D3 docs, CI, manual evidence, exit review | Traceability audit | Planned |

## Existing reusable foundations

- D2 responsive shell, navigation, focus, state, error, disclosure, CSP, and IPC foundations.
- Provider admissions and approved resource metadata.
- Secret reference, vault port, keyring adapter, memory vault, and probe service.
- Canonical local OHLCV import and retained lineage.
- Bounded production ingestion with HTTPS and explicit network flag.
- Kraken normalization, raw payload retention, canonical import, attempts, status, reuse, cancellation, and recovery.

## Prohibited implementation shortcuts

- Frontend-maintained provider authorization.
- Credential values in desktop responses, profile files, databases, state, logs, URLs, or evidence.
- Credential presence treated as policy promotion.
- Direct frontend/Rust keychain, HTTP, file, SQLite, or Parquet access.
- Implicit/global network enablement.
- Paid-provider dependence.
- Recommendation, broker, exchange, autonomous, live-order, or real-capital paths.

## Exit blockers

- Complete all implementation slices and automated tests.
- Pass hosted Linux/macOS contributor and package gates.
- Pass macOS ARM64 and Linux x86-64 clean-profile manual acceptance.
- Resolve every security, accessibility, data-integrity, and network-consent defect.
- Retain validation evidence and D3 exit review.
- Obtain explicit owner direction before merge.
