# D7 Manual Acceptance — Visual Strategy Builder and Backtest Lab

Run from a clean profile on macOS ARM64 and Linux x86-64. Record a platform PASS only when every applicable section passes.

## 1. Startup and Boundaries

1. Launch the packaged desktop app from a clean profile.
2. Open the Strategy Builder and Backtest Lab.
3. Confirm the screen states research-only behavior and contains no brokerage, paper-order, live-order, real-capital, credential, or auto-promotion path.

Expected: the lab opens without network or provider account setup and preserves the no-execution boundary.

## 2. Strategy Definition

1. Create a strategy from a guided template.
2. Set name, objective, asset universe, timeframe, entry rule, exit rule, sizing, risk control, and cost assumptions.
3. Save the strategy.
4. Edit a rule and save again.

Expected: the edit creates a new immutable version; older versions remain inspectable.

## 3. Validation

1. Enter an invalid rule combination.
2. Enter a look-ahead or future-data expression.
3. Select a dataset/timeframe combination that lacks required observations.

Expected: validation fails before execution with clear messages and no plausible backtest result.

## 4. Backtest Execution

1. Run a valid strategy against retained local/sample/cached governed data.
2. Confirm the run records dataset revision, strategy version, assumptions, engine, fidelity level, benchmark, and warnings.
3. Cancel a longer run, if available.
4. Restart the app and inspect retained runs.

Expected: completed, failed, and cancelled states are durable and unambiguous.

## 5. Result Inspection

1. Inspect metrics, equity curve, drawdowns, trade list, exposure, benchmark comparison, and assumptions.
2. Use keyboard and pointer controls to select synchronized chart/table observations.
3. Confirm x-axis and y-axis labels remain readable and useful.
4. Confirm displayed/downsampled views do not change authoritative values.

Expected: chart and table values agree and the selected observation is reviewable without relying on a single inaccessible surface.

## 6. Sensitivity and Walk-Forward

1. Run a bounded parameter sensitivity analysis.
2. Run a walk-forward or out-of-sample evaluation.
3. Inspect train/test ranges, budget limits, overfitting warnings, and result ordering.

Expected: partitions are explicit, future observations are not reused, and warnings are visible.

## 7. Evidence and Export

1. Prepare full-resolution backtest evidence export.
2. Verify schema version, producer version, digest, assumptions, warnings, metrics, and result references.
3. Confirm private local paths, credentials, and provider account details are absent.

Expected: the export is reproducible evidence, not a self-contained provider-data package.

## 8. D6 Project Integration

1. Pin a strategy definition and a backtest result into a D6 project.
2. Restart the app and reopen the project.
3. Confirm pins remain typed, degraded states are visible if a referenced result is unavailable, and provider data is not duplicated.

Expected: D7 evidence integrates with D6 without mutating source results.

## 9. Profile Isolation and Ownership

1. Open the same profile/project from a second window or process where supported.
2. Open a different clean profile.
3. Return to the original profile after releasing ownership.

Expected: concurrent mutation fails closed; separate profiles do not share strategy or result state.

## 10. Accessibility and Responsiveness

1. Navigate the full lab with keyboard only.
2. Confirm visible focus, labels, reduced-motion, forced-colors, and screen-reader names.
3. Resize to 320 CSS px and 680 CSS px widths.

Expected: no clipped controls, unreachable actions, overlapping charts/tables, or inaccessible result inspection.

## 11. Offline Acceptance

1. Disable network access.
2. Reopen retained strategies and runs.
3. Run against local/sample/cached governed data.

Expected: D7 remains usable without paid providers, network access, external accounts, or credentials.
