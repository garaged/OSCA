# D3 Manual Acceptance — Data Sources, Credentials, Import, and Acquisition

- **Status:** Procedure ready; execution pending
- **Platforms:** macOS ARM64 and Linux x86-64
- **Safety:** Use disposable profiles, synthetic/local fixtures, a disposable test credential value, and public Kraken endpoints only. Do not use brokerage, exchange-private, real-capital, or production secrets.

## Preconditions

1. Check out the final D3 branch head.
2. Install the locked Python environment, Node 22, Rust, and platform Tauri prerequisites.
3. Use an isolated desktop-state root and disposable profile outside the repository.
4. Confirm the OS credential backend is available.
5. Run all automated Python, frontend, Rust, OpenSpec, architecture, and secret-scan gates first.

## Evidence record

Retain date, OS/version, architecture, commit, tool versions, screenshots, keyboard/screen-reader notes, profile path with private components redacted, credential backend state, import/acquisition identities, defects, and final disposition. Do not commit secret values or private path-bearing screenshots.

## Acceptance checklist

### 1. D2 regression and clean first run

- Launch with empty D3 desktop state.
- Complete profile creation/open and synthetic sample import.
- Confirm permanent research-only, local-storage, optional-network, and no-live-execution disclosures remain visible.
- Confirm no provider or credential action is required for the sample path.

### 2. Data Sources navigation and provider catalog

- Open Data Sources by keyboard and pointer.
- Confirm provider rows identify admission, approved resources, credential mode, credential state, network requirement, evidence date, rationale, findings, and available actions.
- Confirm Kraken public spot OHLC is approved/no-key/internal-use-only.
- Confirm Twelve Data, Alpha Vantage, and Nasdaq Data Link remain `needs_evidence` and cannot run acquisition.
- Confirm FRED remains policy blocked.
- Confirm credential presence is not described as provider authorization.

### 3. Credential-store unavailable state

- Run with an unavailable or denied test vault backend.
- Confirm credential actions fail closed with safe remediation.
- Confirm no plaintext file fallback is offered or created.
- Confirm the shell, offline import, sample path, and Kraken no-key path remain usable as applicable.

### 4. Credential store, probe, replace, and delete

Using a disposable provider test reference and disposable secret value:

- Store the credential.
- Confirm the field clears and the value never reappears.
- Probe and confirm only `available`/presence metadata is returned.
- Replace with a second value and confirm no old/new value appears in UI, logs, state, profile files, SQLite, Parquet, or evidence.
- Delete after explicit confirmation.
- Probe and confirm `missing`.
- Restart and confirm presence/missing state is read from the OS vault rather than browser state.

### 5. Credential does not promote provider

- Store a credential for a `needs_evidence` provider.
- Confirm admission remains `needs_evidence` and acquisition remains unavailable.
- Confirm promotion blockers and evidence requirements remain visible.
- Delete the credential and confirm admission is unchanged.

### 6. Governed local CSV import

- Use a disposable valid CSV fixture and explicit symbol/timeframe/source/calendar metadata.
- Confirm import works with networking disabled and no credential.
- Confirm canonical SQLite metadata and Parquet payload are retained.
- Confirm provenance, row count, hashes, and dataset revision are displayed.
- Repeat the same import and confirm canonical idempotency behavior.
- Test invalid path, malformed CSV, invalid timeframe, and incompatible rows; confirm no false success or partial accepted profile state.

### 7. Kraken request setup and explicit network consent

- Select Kraken public spot OHLC and a disposable crypto request such as `XBTUSD` with a supported timeframe.
- Before consent, confirm submit is blocked and no provider network request occurs.
- Explicitly enable networking for the request and submit.
- Confirm no credential is requested or used.
- Confirm the UI states internal-use-only and redistribution disabled.

### 8. Kraken success evidence

For a successful request, confirm display of:

- request, correlation, acquisition, and job identifiers;
- provider, resource, symbol, timeframe, venue, and provider pair mapping;
- status, stage, progress, attempts, and duration;
- raw payload URI/hash and canonical payload/metadata URI;
- canonical row count and dataset revision;
- parser/normalizer versions and source attribution;
- internal-use-only, redistribution disabled, recommendations disabled, broker execution disabled, and real-capital execution disabled.

Restart and confirm retained evidence remains inspectable without another network request.

### 9. Reuse and retry

- Repeat an equivalent successful request and confirm the canonical service reports reused evidence rather than duplicating an equivalent dataset.
- Exercise a retryable provider failure using the documented test/fake path or controlled network interruption.
- Confirm retry appears only when remediation supports it and does not claim success before retained evidence exists.

### 10. Cancellation and recovery

- Exercise cancellation before provider retrieval through the documented test/control path.
- Confirm retained `cancelled` status and no dataset-success claim.
- Exercise interrupted-job recovery through the focused automated recovery test or supported manual fixture.
- Confirm recovered/reused state and stable identifiers are honest.
- Confirm no force-delete or hidden retry loop is offered.

### 11. Distinct failures

Verify distinct surfaces for policy blocked, credential missing/denied, quota blocked, provider unavailable, partial, stale, invalid, corrupt, cancelled, and failed outcomes using deterministic test fixtures where live reproduction is unsafe.

Confirm each shows bounded findings/remediation, does not expose raw stack traces or secrets, and only shows retry when safe.

### 12. Network observation

- With networking disabled, observe processes and confirm no unexplained external provider connection during catalog, credential, profile, sample, local import, or evidence inspection.
- During the explicitly consented Kraken request, confirm the provider connection is limited to expected HTTPS behavior.
- Confirm no telemetry, broker, exchange-private, recommendation, or order endpoint is contacted.

### 13. Keyboard, focus, and screen reader

Using keyboard only and VoiceOver/Orca:

- Navigate Data Sources, provider rows, credential actions, import wizard, request setup, progress, evidence, warnings, and confirmations.
- Confirm page-heading focus after navigation, error-summary focus after failed submission, and confirmation focus for delete/cancel.
- Confirm status changes are announced without excessive repetition.
- Confirm secret values are never announced after submission.

### 14. Responsive, motion, and appearance

At approximately 320, 680, and normal desktop widths:

- Confirm no page-level horizontal overflow.
- Confirm tables/cards reflow without hiding policy or safety information.
- Confirm paths/hashes wrap safely and actions remain reachable.
- Test light/dark, reduced motion, and high-contrast/forced-colors support.
- Confirm no state depends only on color, animation, hover, or pointer use.

### 15. Permanent prohibited-boundary inspection

Confirm there is no:

- automatic provider promotion;
- secret reveal/export/copy-back behavior;
- plaintext credential file or database storage;
- frontend/Rust generic keychain, HTTP, file, shell, SQLite, or Parquet access;
- recommendation generation;
- broker/exchange connection;
- autonomous execution;
- order submission or real-capital state;
- provider data redistribution claim.

Any discrepancy is release-blocking.

## Platform disposition

For each platform record `PASS` only when every applicable item passes and all defects are fixed or explicitly block D3 exit.
