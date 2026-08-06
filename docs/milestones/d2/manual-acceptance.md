# D2 Manual Acceptance — Desktop Shell and User Experience Foundation

- **Status:** Procedure ready; execution evidence pending
- **Platforms:** macOS Apple Silicon and Linux x86-64
- **Audience:** Maintainers and early desktop testers
- **Safety:** Use only disposable local profiles. Do not enter provider, broker, exchange, or real-capital credentials.

## Preconditions

1. Check out `agent/d2-desktop-shell`.
2. Install Python 3.13, `uv`, Node.js 22, npm, Rust, and the platform Tauri prerequisites.
3. Confirm no other OSCA desktop process uses the disposable profile.
4. Use a profile path outside the repository, for example:
   - macOS: `$HOME/Library/Application Support/OSCA-D2-Acceptance/profile`
   - Linux: `$HOME/.local/share/osca-d2-acceptance/profile`

Run automated gates first:

```bash
uv sync --locked
uv run ruff check src/osca/desktop_api scripts/run_desktop.py tests/test_d1_desktop_api.py tests/test_d2_desktop_api.py tests/test_desktop_launcher.py
uv run mypy src/osca/desktop_api scripts/run_desktop.py
uv run pytest tests/test_d1_desktop_api.py tests/test_d2_desktop_api.py tests/test_desktop_launcher.py

cd apps/desktop
npm ci
npm run build
npm test
cd src-tauri
cargo fmt --check
cargo test --all-targets --all-features
cargo clippy --all-targets --all-features -- -D warnings
```

## Start the desktop application

From the repository root:

```bash
uv run python scripts/run_desktop.py
```

This launcher sets `OSCA_DESKTOP_PYTHON` to the locked `uv` interpreter before starting Tauri. Do not use arbitrary system `python3` for acceptance. Configure `OSCA_DESKTOP_SIDECAR` only when validating a packaged sidecar candidate.

## Acceptance checklist

### 1. Clean first run

- Remove the disposable profile and desktop preference state.
- Launch OSCA.
- Confirm the first screen says **Welcome to OSCA**.
- Confirm disclosures are visible before any create/open action:
  - research and simulation, not financial advice;
  - local machine storage;
  - network access is optional and explicit;
  - bundled sample requires no provider account;
  - no D2 credential entry;
  - recommendations unavailable;
  - broker, exchange, autonomous, and real-capital execution disabled.
- Confirm Home and System are available.
- Confirm Research and Evidence are labelled **Later** and are not actionable.

### 2. Keyboard and focus

Using only the keyboard:

- Tab to **Skip to main content**, activate it, and confirm focus reaches main content.
- Navigate between Home and System.
- Confirm focus moves to the destination page heading.
- Reach every profile input/button and all available navigation controls.
- Submit an empty profile path and confirm focus moves to the action error summary.
- Confirm visible focus is never clipped or hidden.
- Confirm disabled/deferred destinations do not enter the tab order as fake controls.

### 3. Responsive shell

Resize the content area to approximately 320 CSS pixels, 680 pixels, and a normal desktop width.

Confirm:

- no horizontal page scrolling caused by the shell;
- navigation remains readable and reachable;
- path values wrap instead of overflowing;
- buttons remain usable without overlap;
- permanent safety boundaries remain visible;
- no information exists only in a hover tooltip.

### 4. Profile inspection safety

Enter an absolute path that does not exist and choose **Inspect only**.

Confirm:

- inspection reports that the profile does not exist/cannot open;
- the target directory was not created;
- actionable findings are visible;
- no success/open claim is shown.

Create a non-empty directory with a sentinel file, enter that path, and choose **Create new profile**.

Confirm:

- creation fails;
- the sentinel remains byte-for-byte unchanged;
- no `config.json` is added;
- the UI reports a non-retryable safety error.

### 5. Profile create, select, and open

Enter a new absolute disposable path and choose **Create new profile**.

Confirm:

- profile and data directories are created through Python;
- `config.json` is versioned;
- network, recommendation, broker, autonomous, and real-capital flags are false;
- the app reports the profile open only after validation;
- the profile appears under **Known profiles** after restart.

Select the known profile without opening it.

Confirm the UI distinguishes **selected** from **open**.

Open it and confirm compatibility/storage/lock findings are clear.

### 6. Lock contention

With one process holding the bounded profile mutation lock, attempt to open/import from another process or execute the focused lock test.

Confirm:

- the competing mutation fails closed as `profile_locked`;
- no force-unlock action is offered;
- existing profile content remains unchanged;
- guidance instructs the user to close the other OSCA process and retry.

### 7. Synthetic sample import

Open the disposable profile and choose **Import synthetic sample** twice.

Confirm:

- the UI labels the sample synthetic;
- symbol is `AAPL-SYNTHETIC`;
- row count is 10;
- network used is **No**;
- credential required is **No**;
- the dataset revision identity is identical after the second import;
- a governed Parquet payload and SQLite metadata file exist under the profile storage root;
- metadata source URI is `bundled-synthetic://osca/d2/aapl-daily-v1`;
- no UI copy describes the sample as actual AAPL market history.

### 8. System diagnostics and failure states

Open System with and without a selected profile.

Confirm it displays:

- protocol and sidecar status;
- package/Python/platform values or explicit unknown values;
- profile readiness or an honest empty state;
- network policy disabled unless a later explicit capability enables it;
- provider setup deferred to D3;
- recommendations unavailable;
- live execution disabled.

Stop or misconfigure the Python sidecar and relaunch.

Confirm:

- the shell/safety boundaries remain visible;
- the application reports unavailable rather than ready;
- retry appears only for the retryable sidecar error;
- no raw secret, environment dump, sidecar stderr, or ordinary-user stack trace is displayed.

### 9. Motion, color, and screen reader

- Enable reduced motion and repeat navigation/action state changes; confirm no essential information depends on animation.
- Test system light and dark schemes.
- Test high-contrast/forced-colors mode where supported.
- Verify text, controls, focus rings, badges, errors, and panel boundaries remain distinguishable.
- With VoiceOver on macOS or Orca on Linux, confirm landmarks, page headings, labels, status messages, and error summaries are announced without excessive repetition.

### 10. Permanent deferred-boundary inspection

Inspect UI, diagnostics responses, logs, and generated files. Confirm there is no:

- provider or credential setup surface;
- implicit network request;
- recommendation generation;
- broker or exchange connectivity;
- autonomous execution;
- order submission or real-capital state;
- frontend filesystem/SQLite/Parquet access;
- generic Rust shell/filesystem command;
- fake enabled control for a deferred capability.

Any discrepancy is release-blocking.

## Evidence record

For each platform, retain:

- date, OS/version, architecture, Python/Node/Rust versions;
- source commit;
- automated command results;
- screenshots at narrow and desktop widths;
- keyboard and screen-reader notes;
- created profile path and sample dataset revision;
- defects found and linked fixes;
- final pass/fail disposition.

Do not commit the disposable profile, screenshots containing private paths, credentials, or machine-specific secret material.
