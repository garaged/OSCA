# U11 Exit Review

- **Milestone:** U11 first-run and unified operator experience
- **Status:** Complete
- **Implementation PR:** #74
- **Decision gate:** satisfied

## Delivered outcome

U11 provides one canonical first-run path through the primary `osca` CLI:

1. initialize a safe versioned local profile;
2. diagnose runtime, storage, SQLite/Parquet, port, provider, credential, and evidence readiness;
3. acquire admitted no-cost Kraken history or import local CSV/Parquet data;
4. run deterministic analysis, backtest-to-paper evidence, or the retained experiment/diagnostic/validation pipeline;
5. snapshot or start the loopback-only read-only workspace.

No hand-authored JSON or internal `python -m osca.*` command is required by the canonical quickstart.

## Automated acceptance

Focused U11 coverage proves:

- safe versioned initialization and overwrite refusal;
- strict rejection of unknown or unsafe configuration fields;
- actionable pre-init diagnostics;
- writable storage, SQLite, PyArrow, and loopback-port checks;
- explicit Kraken public capability and no-credential no-cost path diagnostics;
- evidence-consistency warnings and healthy retained-evidence discovery;
- primary CLI command discovery;
- canonical aliases delegate to the documented compatibility commands;
- non-loopback workspace startup is rejected;
- recommendation, promotion, broker, autonomous, and real-capital boundaries stay disabled.

Quality run #729 passed on the final pre-acceptance documentation head:

- Ruff;
- strict mypy across the complete source package;
- all tests plus contract, migration, document-link, and architecture checks;
- OpenSpec doctor and strict validation;
- secret scanning.

## Clean-profile manual acceptance

The August 2, 2026 clean-profile run passed the complete canonical U11 path.

### Initialization and pre-workflow diagnostics

- Profile initialized at `.osca/u11-acceptance/profile` with operator contract `osca.operator-init.result` v1.0.0.
- Network access, recommendations, broker connections, and real-capital orders were disabled.
- The initial doctor result had zero failed checks, seven passes, and two expected warnings: the default port was already occupied and no retained evidence existed yet.

### Acquisition and research chain

- Kraken XBTUSD 1d acquisition succeeded through admitted public spot OHLC.
- Dataset revision: `3261fe47-812a-53d8-926e-7a0a801dd18a`.
- Canonical row count: 720 bars, covering 2024-08-12 through 2026-08-01.
- Provider pair key `XXBTZUSD` was verified.
- Current uncommitted bar exclusion, internal-use-only handling, and redistribution-disabled policy were retained.
- Research run: `73ca1f70-c609-4d1b-bf8a-38494bba82df`.
- Experiment: `06df1ba4-5bbf-4b63-9de7-adae56a7b5c1`, status `review_required`.
- Diagnostic status: `review_required`.
- Pipeline status: `diagnostic_not_eligible`, represented in the workspace as `not_eligible`; validation correctly stopped fail-closed.

### Populated diagnostics and workspace

- Final doctor result had zero failures, eight passes, and one non-blocking warning because port 8765 was already in use.
- Evidence consistency passed with five retained items and no workspace warnings.
- Workspace snapshot contract `osca.analyst-workspace.snapshot` v1.1.0 reported:
  - one dataset;
  - one acquisition;
  - one experiment;
  - one diagnostic;
  - one pipeline run;
  - no validation artifact, as expected for a diagnostic-ineligible run.
- Workspace remained read-only, network-disabled, credential-materialization-disabled, production-ingestion-disabled, recommendation-disabled, broker-disabled, and real-capital-disabled.

The occupied-port warning is informational rather than release-blocking because the snapshot path completed successfully and the doctor supplied explicit remediation to choose another port for server startup.

## Compatibility policy

The following compatibility entry points remain supported through U13 release-candidate acceptance:

- `local-ohlcv-import` → `import-data`;
- `demo-research-report` → `analyze`;
- `backtest-paper-run` → `backtest`;
- `osca-research-pipeline` / module entry point → `osca research-pipeline`;
- analyst-workspace module entry point → `osca workspace`.

Removal requires a later documented decision, release note, and compatibility evidence.

## Acceptance checklist

### Initialization and diagnostics

- [x] `osca init` creates versioned configuration and storage without hand-authored JSON.
- [x] Safe defaults keep network implicit access, recommendations, promotion, brokers, autonomous execution, and real-capital orders disabled.
- [x] Unsafe or unknown configuration fields fail validation.
- [x] `osca doctor` returns structured checks and remediation.
- [x] Runtime, storage, SQLite, PyArrow, port, provider, credential, and evidence consistency are covered.

### Unified primary workflow

- [x] Acquisition is available through `osca historical-data fetch` with explicit network opt-in.
- [x] Offline import is available through `osca import-data`.
- [x] Deterministic analysis is available through `osca analyze`.
- [x] Backtest-to-paper evidence is available through `osca backtest`.
- [x] Experiment, diagnostic, and optional human-gated validation use `osca research-pipeline`.
- [x] Workspace snapshot/server startup use `osca workspace`.

### Compatibility and documentation

- [x] Compatibility aliases are retained through U13.
- [x] Canonical-to-compatibility delegation is covered automatically.
- [x] zsh, Bash, and PowerShell quickstarts are documented.
- [x] Root README uses the canonical U11 workflow.
- [x] Central manual-testing guide is reconciled through U11.

### Quality and manual evidence

- [x] Final hosted Quality is green on the implementation-closeout head.
- [x] Clean-profile initialization and pre-workflow doctor evidence are retained.
- [x] One acquisition-to-research chain is retained.
- [x] Populated-profile doctor and workspace snapshot evidence are retained.
- [x] Safety boundaries are confirmed in the retained outputs.

## Residual limitations

- U11 is a technically capable operator experience rather than a graphical onboarding wizard.
- Network acquisition still requires explicit provider selection and opt-in.
- No no-cost equity provider is admitted; CSV/Parquet import remains the governed equity fallback.
- Packaging and clean-machine installation lifecycle are owned by U12.

## Exit decision

U11 is complete, accepted, and ready to merge. The next milestone is U12 clean-machine packaging and upgrade safety.
