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

The final closeout documentation passed the complete hosted Quality suite: Ruff, strict mypy, all tests and repository checks, OpenSpec strict validation, and secret scanning.

## Clean-profile manual acceptance

The August 2, 2026 clean-profile run passed the complete canonical U11 path.

- Profile contract: `osca.operator-init.result` v1.0.0.
- Initial doctor: zero failures, seven passes, two expected warnings.
- Kraken XBTUSD 1d acquisition: succeeded, 720 bars.
- Dataset revision: `3261fe47-812a-53d8-926e-7a0a801dd18a`.
- Research run: `73ca1f70-c609-4d1b-bf8a-38494bba82df`.
- Experiment: `06df1ba4-5bbf-4b63-9de7-adae56a7b5c1`, `review_required`.
- Diagnostic: `review_required`.
- Pipeline: `diagnostic_not_eligible`; validation stopped fail-closed.
- Final doctor: zero failures, eight passes, one informational occupied-port warning.
- Workspace: five retained items, no warnings, read-only and all recommendation/execution boundaries disabled.

The occupied-port warning is not release-blocking because the snapshot completed successfully and the doctor supplied explicit remediation for server startup.

## Acceptance checklist

- [x] Safe versioned initialization and structured diagnostics.
- [x] Canonical acquisition/import, analysis, backtest, research pipeline, and workspace commands.
- [x] Compatibility aliases and cross-shell quickstarts.
- [x] Root README and central manual-testing reconciliation.
- [x] Complete hosted Quality.
- [x] Clean-profile acquisition-to-research evidence.
- [x] Populated doctor and workspace evidence.
- [x] Disabled safety boundaries.

## Residual limitations

- U11 is a technically capable operator experience rather than a graphical onboarding wizard.
- Network acquisition still requires explicit provider selection and opt-in.
- No no-cost equity provider is admitted; CSV/Parquet import remains the governed equity fallback.
- Packaging and clean-machine installation lifecycle are owned by U12.

## Exit decision

U11 is complete, accepted, and ready to merge. The next milestone is U12 clean-machine packaging and upgrade safety.
