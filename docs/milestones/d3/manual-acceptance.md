# D3 Manual Acceptance — Data Sources, Credentials, Import, and Acquisition UX

- **Status:** Passed on supported platforms
- **Platforms:** macOS Apple Silicon and Linux x86-64
- **Accepted source:** PR #83 D3 branch after acceptance fixes
- **Execution date:** 2026-08-06 (America/Mexico_City)

## Accepted result

The repository owner reported the complete procedure passed on:

- macOS ARM64, including packaged-application smoke, accessibility, responsive layout, network observation, persistence, recovery, and failure handling;
- Linux x86-64, including the equivalent desktop, accessibility, package, network, persistence, recovery, and failure checks.

Machine-local screenshots, environment captures, network observations, paths, and profile data remain outside the repository to avoid publishing host-specific or private information.

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

## Accepted coverage

### 1. Clean start and navigation

- Application opened without an existing selected profile.
- Workspace and Data Sources were keyboard reachable.
- Focus moved predictably when changing areas.
- Permanent research-only and no-live-execution boundaries remained visible.

### 2. Responsive and accessible behavior

The Data Sources surface passed at approximately 320 CSS pixels, 680 CSS pixels, and normal desktop width. Labels, keyboard access, visible focus, status/error handling, reduced motion, light/dark appearance, high contrast, VoiceOver on macOS, and Orca on Linux were accepted.

### 3. Provider catalog and policy separation

Provider policy and credential state remained inspectable without an open profile. Kraken was limited to the approved public spot-OHLC resource. Providers needing rights evidence remained blocked despite credential presence. Offline sample and local CSV import remained available without a paid account.

### 4. Profile and offline import

The isolated profile was created, opened, restarted, and reused safely. Valid local OHLCV CSV import succeeded without networking or credentials. Repeated import behaved deterministically. Malformed, missing, and unsafe inputs failed without partial persistence.

### 5. Credential lifecycle

Disposable fake credentials were stored, probed, replaced, and deleted through the OS vault. Secret values cleared from the UI and did not appear in logs, URLs, profile state, analytical storage, or evidence. Credential presence did not promote provider admission.

### 6. Kraken request-scoped acquisition

Acquisition without explicit consent failed before networking. A consented Kraken public OHLC request succeeded without an API key. The operation remained synchronous and request-scoped, consent reset after use, repeated requests exhibited canonical reuse/idempotency, and retained evidence showed the expected provider, symbol, timeframe, status, revision, and row-count information.

### 7. Retained evidence and restart

Completed acquisition evidence remained available after application restart and profile reopening. Only evidence under the selected profile's canonical storage root was listed.

### 8. Network observation

Offline import, credential operations, and provider-catalog inspection produced no unexpected external provider traffic. External traffic occurred only during the explicitly consented Kraken request. Loopback development connections were accepted.

### 9. Failure and recovery behavior

Missing and malformed CSVs, provider/network failures, profile lock contention, restart recovery, and concurrent profile mutation protection failed safely without corrupting valid profile data or evidence. Recommendations, broker/exchange connectivity, autonomous execution, live orders, and real-capital execution remained unavailable.

## Defects discovered and resolved during acceptance

- Vite test servers collided on the default HMR WebSocket port; frontend tests now run deterministically and avoid unnecessary dependency discovery.
- The top-right mode switch overlapped safety status pills at intermediate widths; responsive layout now reserves or reflows the control.
- Generic input styling made the Kraken consent checkbox effectively invisible on macOS; it now has native sizing, explicit association, focus styling, and a distinct consent row.
- The frontend used `acquisition.submit` while the Python allow-list exposed `acquisition.run`; the frontend now uses the canonical method.
- The frontend parsed the acquisition result without accounting for the Python `evidence` envelope; parsing now matches the contract.
- The retained-evidence parser expected `evidence` while Python returns `acquisitions`; the parser and regression checks now match the authoritative response.

## Exit rule disposition

The supported-platform manual gate is satisfied. D3 final exit remains conditional on refreshed hosted validation passing and explicit repository-owner direction before merge.
