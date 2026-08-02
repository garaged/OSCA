# U11 Exit Review

- **Milestone:** U11 first-run and unified operator experience
- **Status:** Automated conformance complete; clean-profile acceptance pending
- **Implementation PR:** #74
- **Decision gate:** clean-profile end-to-end acceptance

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

Quality run #727 passed on commit `f72eae9fb9e7ddb1b4666576e1e6b88c99e55446`:

- Ruff;
- strict mypy across the complete source package;
- all tests plus contract, migration, document-link, and architecture checks;
- OpenSpec doctor and strict validation;
- secret scanning.

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
- [ ] Clean-profile initialization and pre-workflow doctor evidence are retained.
- [ ] One acquisition/import-to-research chain is retained.
- [ ] Populated-profile doctor and workspace snapshot evidence are retained.
- [ ] Safety boundaries are confirmed in the retained outputs.

## Residual limitations

- U11 is a technically capable operator experience rather than a graphical onboarding wizard.
- Network acquisition still requires explicit provider selection and opt-in.
- No no-cost equity provider is admitted; CSV/Parquet import remains the governed equity fallback.
- Packaging and clean-machine installation lifecycle are owned by U12.

## Exit decision

U11 implementation and automated conformance are complete. Final closure requires only the clean-profile evidence described in `manual-acceptance.md`.
