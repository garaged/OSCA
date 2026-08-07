# D3 Specification — Data Sources, Credentials, Import, and Acquisition UX

- **Status:** In progress
- **Governing role:** Product, architecture, security, data-governance, and quality authority
- **Purpose:** Define implementation-ready behavior for provider capability discovery, secure credential references, governed local import, Kraken public historical acquisition, job inspection, cancellation, retry, recovery, and evidence display.
- **Governing intent:** `docs/milestones/d3/intent.md`
- **Dependencies:** D2 shell and desktop application API; existing provider admission, security-vault, local import, production-ingestion, and historical-acquisition services
- **Downstream consumers:** Python desktop application API, React desktop frontend, automated tests, hosted validation, manual testing, D4-D19

## Problem and context

D2 gives users a safe offline desktop shell, validated profiles, diagnostics, and deterministic synthetic sample data. It deliberately does not expose provider setup, credentials, local-file import, or network acquisition.

OSCA already contains canonical provider admission policy, secret-vault ports and OS-keyring infrastructure, local OHLCV import, bounded production ingestion, and governed Kraken historical acquisition. D3 exposes those capabilities through a versioned desktop application boundary without creating a second provider stack or moving authority into React or Rust.

A saved credential is not provider authorization. Admission status, licensing evidence, account-plan evidence, approved resources, and credential presence are separate states and must remain visibly separate.

## Scope

### In scope

- Data Sources destination and provider catalog.
- Display of provider admission, approved resources, credential mode, evidence date, rationale, findings, and promotion blockers.
- OS-keyring-backed credential store, probe, replace, and delete flows using named secret references.
- No-key Kraken public OHLC capability.
- Governed CSV local OHLCV import wizard.
- Kraken historical acquisition request, progress, evidence, cancellation, retry, and recovery surfaces.
- Explicit per-request network consent and permanent network-status visibility.
- Provenance, raw/canonical evidence, dataset revision, attribution, retention, quota, and remediation display.
- Responsive, keyboard, screen-reader, reduced-motion, light/dark, and error-state behavior inherited from D2.
- Clean-profile manual acceptance on macOS ARM64 and Linux x86-64.

### Out of scope

- Automatic provider promotion or policy mutation.
- Treating credential presence as provider admission.
- Twelve Data, Alpha Vantage, Nasdaq Data Link, or FRED production acquisition without accepted evidence.
- Embedded credentials, environment-variable credential entry, plaintext credential persistence, or secret display after submission.
- Browser/frontend direct access to keychains, files, SQLite, Parquet, provider endpoints, or shell commands.
- Production charting, watchlists, research workspaces, recommendations, broker/exchange connectivity, autonomous execution, live orders, or real-capital execution.
- External redistribution of provider data.

## Terminology

- **Provider admission:** Governing decision describing whether a provider resource is approved, needs evidence, or is policy blocked.
- **Credential state:** Whether an expected named secret reference is present, missing, denied, or unavailable in the OS vault.
- **Capability status:** Result of combining admission, resource, credential, profile, and network prerequisites without changing any underlying authority.
- **Network consent:** Explicit user action attached to one governed acquisition request; not a global implicit opt-in.
- **Acquisition job:** Retained request/status/evidence lifecycle produced by the canonical historical-acquisition service.
- **Promotion evidence:** Licensing, account-plan, data-rights, retention, display, export, and redistribution evidence required before a provider resource can be admitted.

## Behavioral requirements

### D3-BR-001 — Authoritative provider catalog

The desktop application must return provider capability rows from the canonical production-ingestion admission policy. React must not maintain a separate allowlist or infer authorization from provider popularity, credentials, or network availability.

### D3-BR-002 — Separate admission, credential, and operational states

Each provider row must separately expose admission status, approved resources, credential mode, credential state, network requirement, available actions, rationale, findings, evidence timestamp, and terms reference. Saving a credential must not change admission or approved resources.

### D3-BR-003 — Honest free and offline paths

The Data Sources surface must identify governed CSV import and bundled synthetic sample as credential-free offline paths. Kraken public spot OHLC must be identified as a no-key network path. Paid or evidence-blocked providers must not be required for core D3 usability.

### D3-BR-004 — Secure credential references

Credential values may be accepted only by a versioned Python application method and stored through the `SecretVault` port. The desktop response may return a display-safe secret reference and state but never the value. Values must not enter profile configuration, SQLite, Parquet, desktop preference state, ordinary logs, exception text, URLs, command arguments, analytics, or retained evidence.

### D3-BR-005 — Credential lifecycle

The UI must support store/replace, probe, and delete for providers whose policy declares `named-secret-reference`. Empty values are rejected. Replacement is explicit. Delete confirms the target provider/reference. Vault unavailable or denied states fail closed with remediation and no plaintext fallback.

### D3-BR-006 — Provider-policy enforcement

Only an approved provider resource may be submitted to production acquisition. `needs_evidence` and `policy_blocked` providers remain non-runnable even when a credential is present. Warnings and promotion evidence cannot silently mutate admission policy.

### D3-BR-007 — Explicit network consent

Every acquisition submission must carry explicit `network_access_enabled=true` from a deliberate user action. Catalog inspection, credential operations, profile operations, local import, sample import, job inspection, and retained evidence inspection must not require provider network access.

### D3-BR-008 — Governed local import wizard

The desktop application must expose canonical local OHLCV CSV import with an absolute selected path, explicit symbol, timeframe, source URI, and calendar assumption. Python validates and imports the file; React and Rust do not parse it. Validation failures must not create a successful dataset claim.

### D3-BR-009 — Kraken acquisition request

D3 must expose the existing Kraken public spot OHLC acquisition for crypto symbols and supported intervals `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, and `1d`. Requests must use canonical profile storage, HTTPS, provider admission, bounded transport, normalization, and local import services.

### D3-BR-010 — Job progress and retained evidence

The UI must present stable job/request/correlation identifiers; status; stage; progress; attempts; duration; provider pair; row count; raw and canonical evidence locations; hashes; dataset revision; attribution; quota state; findings; remediation; and safety flags from typed application responses. Unknown values remain unknown.

### D3-BR-011 — Cancellation, retry, and recovery

Cancellation must be explicit and fail closed. Retry must create or reuse a governed request according to canonical idempotency behavior. Interrupted retained jobs must be recoverable by the existing acquisition service. The UI must never claim that cancellation stopped a completed operation or that retry succeeded before evidence exists.

### D3-BR-012 — Failure and quota handling

Policy blocked, credential blocked, quota blocked, provider unavailable, partial, stale, invalid, corrupt, cancelled, and failed outcomes must remain distinct. Retry is shown only where remediation supports it. Raw provider payload or stack traces are not shown to ordinary users.

### D3-BR-013 — Narrow desktop authority boundary

React continues to call the single Rust `desktop_request` command and versioned Python methods. D3 does not add generic filesystem, shell, database, environment, keychain, or HTTP capabilities to React or Rust.

### D3-BR-014 — Accessibility and responsive acquisition UX

Catalog, credential, import, acquisition, progress, evidence, warning, and error controls must remain usable by keyboard and screen reader at 320 CSS pixels and normal desktop widths. Status must not depend on color or motion alone. Focus moves to page headings, submitted-action errors, and destructive-action confirmations as appropriate.

### D3-BR-015 — Permanent financial and execution boundary

No D3 contract or UI may enable recommendations, broker/exchange connections, autonomous execution, order submission, or real-capital execution. Provider acquisition is data retrieval only.

## Inputs and preconditions

- A compatible writable profile is open for import or acquisition.
- Provider policy remains canonical in `osca.production_ingestion.policy`.
- Credential storage uses `osca.security.application.SecretVault`; production desktop composition uses `KeyringVault`.
- Kraken acquisition uses the existing `HistoricalAcquisitionRequest` and service.
- Local import uses the existing canonical OHLCV import service.
- Desktop protocol additions remain compatible within protocol `1.x` unless an explicit protocol decision is accepted.

## Outputs and postconditions

- Users can see why each provider capability is available or blocked.
- Users can save/delete a credential without the secret appearing in desktop responses or analytical storage.
- Users can import governed CSV evidence entirely offline.
- Users can explicitly run approved Kraken public acquisition and inspect retained evidence.
- Admission policy remains unchanged by UI actions.
- All failures preserve a safe profile and honest capability state.

## Invariants

- Python is authoritative for provider policy, credentials, import, acquisition, evidence, and safety status.
- Secret values never cross back to React.
- Network access is request-scoped, explicit, and disabled by default.
- Offline import and sample paths remain usable without credentials or paid services.
- Provider data remains internal-use-only where policy says so; redistribution remains disabled.
- No recommendation or execution path exists.

## Failure and degradation behavior

| Failure | Required behavior | Recovery |
|---|---|---|
| Vault unavailable/denied | Credential action fails closed; no plaintext fallback | Show OS credential-store remediation and retry probe |
| Credential missing | Admission remains visible; credentialed action unavailable | Store the named credential or use free/offline path |
| Provider needs evidence | Credential may be managed, acquisition remains blocked | Review and accept exact promotion evidence outside automatic D3 flow |
| Provider policy blocked | Acquisition control absent/disabled | Use approved provider or local import |
| Network not consented | No provider request is made | Explicitly enable the single acquisition request |
| Provider unavailable/quota | Retain typed failure and safe evidence | Retry only after indicated recovery window |
| Invalid symbol/pair/range | No dataset success claim | Correct inputs and resubmit |
| Partial/stale result | Preserve evidence with warning status | Adjust range/freshness expectations or retry |
| Corrupt payload | Retain corruption finding; do not use canonical data | Retry retrieval; inspect evidence |
| Cancellation | Retain cancelled state and no false success | Submit a new governed request |
| Sidecar failure | Shell and safety disclosures remain visible | Retry typed request or inspect System |

## Security and privacy

- Credential input controls use password semantics and are cleared after submission.
- Desktop API errors are stable, bounded, and display-safe.
- Secret references use validated namespaces and names.
- Credential values are never interpolated into messages, endpoint URLs, logs, or evidence.
- Keyring backend failures are mapped to unavailable/denied outcomes without backend exception detail leakage.
- Provider HTTP endpoints must be HTTPS and bounded by existing ingestion limits.
- Telemetry remains disabled by default.

## Data, identity, and lineage

- Local import retains source URI, format, calendar assumption, producer identity, hashes, and dataset revision.
- Kraken acquisition retains provider admission, raw payload identity, normalization versions, canonical revision, predecessor/supersession, attempts, findings, and attribution.
- Credential metadata is not analytical evidence and stores no value.
- D3 creates no alternate SQLite or Parquet schema outside canonical services.

## Acceptance criteria

| ID | Criterion | Verification |
|---|---|---|
| D3-AC-001 | Provider catalog exactly reflects canonical policy and explains blocked states | Contract/component tests and manual inspection |
| D3-AC-002 | Offline sample and CSV import remain usable with no credentials or network | Integration and manual acceptance |
| D3-AC-003 | Keyring credential store/probe/delete never returns or persists secret values | Unit, architecture, redaction, and manual tests |
| D3-AC-004 | Credential presence never promotes a provider | Policy-negative tests |
| D3-AC-005 | Kraken public acquisition requires explicit network consent and no key | Integration and network-negative tests |
| D3-AC-006 | Supported symbols/timeframes produce retained canonical evidence or honest typed failure | Integration tests |
| D3-AC-007 | Cancellation, retry, idempotent reuse, and interrupted-job recovery are tested | Job lifecycle tests |
| D3-AC-008 | Policy/quota/provider/partial/stale/invalid/corrupt/cancelled states remain distinct | Contract and component tests |
| D3-AC-009 | React/Rust gain no generic file, keychain, HTTP, shell, or database authority | Architecture tests |
| D3-AC-010 | Keyboard, VoiceOver, Orca, narrow-width, reduced-motion, and light/dark acceptance pass | Supported-platform manual evidence |
| D3-AC-011 | Recommendations and every execution path remain unavailable | Negative tests and manual inspection |
| D3-AC-012 | Hosted Linux/macOS gates, traceability, limitations, and exit review are retained | CI and governance audit |

## Test strategy

- Python contract tests for every D3 desktop method and malformed input.
- Vault tests using memory/fake backends; production composition tests for keyring without storing real secrets in CI.
- Redaction tests proving secrets never appear in responses, exceptions, logs, state, profile files, or evidence.
- Provider-policy and capability-resolution tests.
- Local import validation, idempotency, lineage, and rollback tests.
- Kraken acquisition tests with deterministic fake transport for success, quota, provider, invalid, partial, stale, cancellation, retry, and recovery.
- TypeScript response validation and React state/render tests.
- Architecture tests preserving the narrow Rust/frontend boundary.
- Manual macOS ARM64 and Linux x86-64 acceptance using disposable profiles and non-production test credentials only.

## Documentation requirements

- Add D3 requirements catalog, OpenSpec change, traceability, manual acceptance, validation evidence, and exit review.
- Update desktop capability map, product traceability, development guide, and user-facing provider/import documentation.
- Document credential deletion and OS-vault remediation without exposing secret values.
- Document Kraken internal-use attribution and redistribution restriction.

## Resolved architecture decisions

- Reuse canonical provider admission and acquisition services; do not build a desktop-only provider stack.
- Reuse `SecretVault` and `KeyringVault`; no new credential dependency or plaintext fallback.
- Provider admission remains repository-governed, not user- or credential-mutated.
- Kraken public OHLC is the D3 production acquisition path; governed CSV and bundled sample remain the universal free/offline paths.
