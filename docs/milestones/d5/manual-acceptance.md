# D5 Manual Acceptance — Charting and Quantitative Analysis Workbench

Run this procedure from a clean profile on each supported D5 platform: macOS ARM64 and Linux x86-64. Use bundled sample data or governed local/cached data so the core acceptance path requires no paid provider and no network access.

Record only generic PASS/FAIL evidence in the repository. Do not commit private filesystem paths, credentials, provider account details, or personal data.

## 1. Launch and safety boundary

1. Build and launch the native desktop application through the documented platform build path.
2. Open or create a clean profile and enter the Workbench.
3. Confirm the surface visibly identifies itself as research/analysis only and provides no recommendation, broker, order, or real-capital action.
4. With network observation enabled, keep the application offline for the local/sample acceptance path and confirm no unexpected provider request occurs.

Expected: Workbench starts from governed local/sample/cached data without a paid service or separately started development server.

## 2. Governed series and range interaction

1. Select a canonical asset with retained/sample OHLCV data.
2. Load a supported timeframe and inspect the displayed dataset revision/provenance context.
3. Change the bounded date/time range.
4. Zoom and pan the visible chart.
5. Inspect price, volume, source row count, filtered row count, displayed row count, and downsampling state.

Expected: chart updates remain bounded and deterministic; purely visual viewport changes do not imply a new dataset or numerical recomputation; provenance and row-count semantics stay visible.

## 3. Chart/table parity

1. Choose at least five visible timestamps spanning the loaded range.
2. For each timestamp, compare chart/keyboard inspection values against the synchronized table for open, high, low, close, volume, and an enabled derived series.
3. Repeat after changing the range and after a downsampled display is active.

Expected: values correspond to the same returned result. No contradictory value is shown between chart and table.

## 4. Indicators

1. Enable a moving-average indicator and change its valid window.
2. Enable at least one additional supported deterministic indicator/metric.
3. Inspect visible parameter, warm-up/evidence, and provenance information.
4. Try an invalid or unsupported parameter combination.

Expected: valid calculations come from the authoritative service; invalid combinations fail visibly rather than being approximated by the frontend.

## 5. Comparisons

1. Add a compatible comparison asset/series over the same declared range.
2. Inspect both canonical identities, timeframes, units/currency semantics, and provenance.
3. Attempt an intentionally incompatible comparison when the UI exposes one.

Expected: compatible comparison is explicit and deterministic; incompatible semantics fail visibly and are never silently joined or normalized.

## 6. Downsampling disclosure

1. Load a range larger than the configured display row budget.
2. Confirm the UI explicitly reports that the display is downsampled and shows source/filtered/displayed counts.
3. Confirm first and last required boundary observations remain represented.
4. Reduce the range until no downsampling is needed.

Expected: the approximation state is obvious and disappears when the full filtered range fits the display budget.

## 7. Full-resolution export

1. While a downsampled display is active, export the tabular evidence and reproduction metadata.
2. Verify the exported data row count represents the full filtered analytical result, not only displayed points.
3. Verify metadata identifies canonical asset, dataset revision, timeframe/range, requested indicators/series, row count, digest/provenance, and export schema/version.
4. Export the visible chart image/SVG if provided and confirm it is clearly presentation evidence rather than the data export.

Expected: display downsampling never truncates the full-resolution analytical export.

## 8. Saved views and profile isolation

1. Create a named workbench view with a range, indicators, pane settings, and a comparison when available.
2. Rename/update it, close/restart the application, and reload it.
3. Confirm the restored view references the same canonical configuration without modifying the underlying dataset.
4. Open a different clean profile and confirm the first profile's saved view is absent.
5. Exercise same-profile concurrent ownership using the established D4 second-window procedure and attempt a saved-view mutation from the non-owner.
6. Release the owner and confirm a subsequent owner can mutate the saved view.

Expected: saved views are profile-scoped, durable, declarative, and protected by the existing ownership/locking boundary.

## 9. Accessibility and responsive layouts

Verify all of the following:

- keyboard-only operation for navigation, range/indicator/view/export controls, and data inspection;
- visible focus and no keyboard trap;
- screen-reader description/summary of the chart plus access to equivalent tabular values (VoiceOver on macOS, Orca on Linux);
- light and dark appearance where platform/application settings support them;
- forced/high-contrast mode retains controls, focus, line distinctions, and status meaning;
- reduced-motion mode removes nonessential animated transitions;
- positive/negative or state differences are not communicated by color alone;
- narrow 320 CSS-pixel layout retains essential controls without inaccessible horizontal loss;
- intermediate 680 CSS-pixel and normal desktop layouts remain usable.

## 10. Performance and packaging

1. Launch the packaged app directly.
2. Load a typical local/cached chart and record whether it becomes usable within the D5 three-second target on acceptance hardware.
3. Exercise range changes, indicators, tables, saved views, and a large downsampled range; confirm ordinary interactions remain responsive and do not produce recurring multi-second freezes.
4. Start a full-resolution export and confirm longer work surfaces progress or a meaningful busy/error state rather than freezing the entire desktop UI.

Expected: typical cached/local workbench load targets p95 under three seconds; large display payloads remain bounded by the configured row budget.

## Acceptance result

Record a platform PASS only when all applicable sections pass. Any numerical disagreement, hidden downsampling, truncated full-resolution export, unexpected network/provider use, accessibility blocker, profile-isolation failure, brokerage/execution path, or recurring unacceptable UI stall blocks D5 exit.
