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

Focused U11 coverage proves safe initialization, strict configuration validation, corrective diagnostics, primary CLI discovery, compatibility delegation, retained-evidence consistency, loopback-only workspace access, and disabled recommendation/execution boundaries.

Quality run #733 passed on final closeout head `c957d3d358e249b0c9b27f7cde0a7a76b9b66d9a`:

- Ruff;
- strict mypy;
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
- Workspace snapshot contract `osca.analyst-workspace.snapshot` v1.1.0 reported one dataset, one acquisition, one experiment, one diagnostic, and one pipeline run.
- No validation artifact was present, as expected for a diagnostic-ineligible run.
- Workspace remained read-only, network-disabled, credential-materialization-disabled, production-ingestion-disabled, recommendation-disabled, broker-disabled, and real-capital-disabled.

The occupied-port warning is informational rather than release-blocking because the snapshot path completed successfully and the doctor supplied explicit remediation to choose another port for server startup.

## Compatibility policy

Compatibility entry points remain supported through U13 release-candidate acceptance. Removal requires a later documented decision, release note, and compatibility evidence.

## Acceptance checklist

- [x] Safe versioned initialization and structured diagnostics.
- [x] Canonical acquisition/import, analysis, backtest, research pipeline, and workspace commands.
- [x] Compatibility aliases and cross-shell quickstarts.
- [x] Root README and central manual-testing reconciliation.
- [x] Final hosted Quality on the final closeout head.
- [x] Clean-profile initialization and pre-workflow doctor evidence.
- [x] One acquisition-to-research chain.
- [x] Populated-profile doctor and workspace snapshot evidence.
- [x] Confirmed disabled safety boundaries.

## Residual limitations

- U11 is a technically capable operator experience rather than a graphical onboarding wizard.
- Network acquisition still requires explicit provider selection and opt-in.
- No no-cost equity provider is admitted; CSV/Parquet import remains the governed equity fallback.
- Packaging and clean-machine installation lifecycle are owned by U12.

## Exit decision

U11 is complete, accepted, and ready to merge. The next milestone is U12 clean-machine packaging and upgrade safety.
