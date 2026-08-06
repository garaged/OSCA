# D3 Manual Acceptance — Data Sources, Credentials, Import, and Acquisition UX

- **Status:** Procedure ready; execution evidence pending
- **Platforms:** macOS Apple Silicon and Linux x86-64
- **Source:** PR #83 head under acceptance

## Preferred Makefile workflow

Run these commands from the repository root:

```bash
make tools
make acceptance-check
make run-clean
```

`make run-clean` removes and recreates only the isolated acceptance directory at `.osca/d3-manual-acceptance`, installs locked dependencies, and launches the desktop application with `OSCA_DESKTOP_STATE_ROOT` pointed at the isolated state directory. It does not modify normal OSCA profiles.

Record environment and source metadata with:

```bash
make acceptance-info | tee .osca/d3-manual-acceptance/evidence/environment.txt
```

Build the native package for the current platform with:

```bash
make build
```

Run `make help` for all available setup, build, test, lint, package, status, and cleanup commands.

## Acceptance paths

The default paths are:

```text
.osca/d3-manual-acceptance/state
.osca/d3-manual-acceptance/profile
.osca/d3-manual-acceptance/evidence
```

Override the root without editing the Makefile:

```bash
make run-clean ACCEPTANCE_ROOT=/absolute/path/to/d3-acceptance
```

## Manual acceptance sequence

### 1. Clean start and navigation

1. Start with `make run-clean`.
2. Confirm the application opens without an existing selected profile.
3. Confirm Workspace and Data Sources are keyboard reachable.
4. Confirm focus moves predictably when changing areas.
5. Confirm permanent research-only and no-live-execution boundaries remain visible.

### 2. Responsive and accessible behavior

Validate the Data Sources surface at approximately:

- 320 CSS pixels
- 680 CSS pixels
- normal desktop width

Confirm:

- no horizontal content loss;
- labels remain associated with controls;
- keyboard navigation reaches every action;
- visible focus is retained;
- status and error messages receive focus or are announced;
- reduced-motion mode removes nonessential transitions;
- light, dark, and forced-colors/high-contrast modes remain usable;
- VoiceOver on macOS or Orca on Linux announces headings, regions, fields, status, and destructive credential actions meaningfully.

### 3. Provider catalog and policy separation

1. Open Data Sources without a profile.
2. Confirm provider policy and credential state remain inspectable.
3. Confirm import, acquisition, and retained evidence explain that a validated profile is required.
4. Confirm Kraken is approved only for the supported public spot-OHLC resource.
5. Confirm providers needing rights evidence remain blocked even after a credential is stored.
6. Confirm offline sample and local CSV import remain available without a paid provider account.

### 4. Profile and offline import

1. Return to Workspace and create the isolated profile shown by `make acceptance-info`.
2. Reopen Data Sources.
3. Import a valid local OHLCV CSV.
4. Confirm symbol, timeframe, source, lineage, revision, and result state are shown.
5. Repeat the same import and confirm idempotent behavior.
6. Attempt malformed and unsafe-path inputs and confirm typed, actionable failures without partial persistence.
7. Observe that no external provider connection occurs during local import.

### 5. Credential lifecycle

Use a disposable non-production credential value only.

1. Store a named credential for a provider whose policy supports named-secret references.
2. Confirm the secret field clears after submission.
3. Confirm only presence/probe metadata returns; the value must never appear in the UI, logs, profile files, ordinary state, databases, URLs, or evidence.
4. Probe the credential.
5. Replace it and probe again.
6. Delete it and confirm the final missing state.
7. Confirm admission status and approved resources do not change throughout the lifecycle.
8. Confirm denied or unavailable OS-vault behavior produces a safe typed error and remediation.

### 6. Kraken request-scoped acquisition

1. Attempt acquisition without selecting the explicit network-consent checkbox.
2. Confirm the request is rejected before provider networking.
3. Select consent for one request and acquire a small public Kraken OHLC dataset.
4. Confirm no API key is requested.
5. Confirm the interface describes the operation as synchronous and does not claim live background progress or active cross-request cancellation.
6. Confirm result status, rationale, provider, symbol, timeframe, internal-use-only status, redistribution-disabled status, and evidence references are shown.
7. Confirm the consent checkbox resets after the request.
8. Repeat the same request and confirm canonical reuse/idempotency behavior.
9. Confirm quota, provider, invalid, corrupt, partial, stale, cancelled, and failed outcomes remain distinguishable when exercised through deterministic tests or controlled failure fixtures.

### 7. Retained evidence and restart

1. Confirm completed acquisition evidence appears in the retained evidence list.
2. Quit the application.
3. Relaunch with `make acceptance-run` without resetting the acceptance root.
4. Return to Data Sources.
5. Confirm the selected profile context reloads from Python-owned state.
6. Confirm retained acquisition evidence remains inspectable.
7. Confirm only evidence beneath the selected profile’s canonical storage root is listed.

### 8. Network observation

During offline import, credential operations, and provider-catalog inspection, observe established connections for OSCA/Tauri/Node/Python processes. Loopback development connections are permitted; unexpected external provider traffic is not.

On macOS:

```bash
/usr/sbin/lsof -nP -iTCP -sTCP:ESTABLISHED \
  | grep -Ei 'osca|tauri|node|python' \
  | tee .osca/d3-manual-acceptance/evidence/network-observation.txt
```

Use the equivalent process/network inspection tool on Linux.

### 9. Failure behavior

Validate:

- missing sidecar produces an actionable application-service error;
- profile lock contention fails safely;
- missing or locked OS credential store fails safely;
- malformed import does not partially persist;
- denied network consent performs no provider request;
- provider failures retain typed evidence without exposing credentials;
- recommendations, broker/exchange connectivity, autonomous execution, live orders, and real-capital execution remain unavailable.

## Evidence record

Retain, without secrets or private home-directory information:

- date;
- operating system and version;
- architecture;
- source commit;
- Python, uv, Node, npm, Rust, and Cargo versions;
- `make acceptance-check` result;
- screenshots at narrow and desktop widths;
- keyboard and screen-reader notes;
- profile root and imported/acquired revision identifiers;
- credential lifecycle result using only redacted presence metadata;
- network observation;
- defects and fixes;
- final PASS or FAIL disposition.

## Exit rule

D3 manual acceptance passes only after both macOS ARM64 and Linux x86-64 complete this procedure, every security, accessibility, data-integrity, and network-consent defect is resolved, and explicit owner acceptance is recorded.
