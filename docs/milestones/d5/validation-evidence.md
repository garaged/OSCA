# D5 Validation Evidence — Production Charting and Quantitative Analysis Workbench

- **Status:** Automated validation passed; macOS ARM64 and Linux x86-64 manual acceptance passed
- **Pull request:** #85
- **Branch:** `agent/d5-charting-quant-workbench`
- **Baseline:** D4 merge `a4e733292ff42775848520afd536d57a18cada1f`
- **Validated implementation candidate:** `12724813d1a542663a5fbdd8649754107a8f3357`

## Automated validation

The final implementation candidate passed:

- Quality run `31731274246`;
- Desktop Foundation run `31731274364`;
- PR aggregate run `31731272397`;
- strict OpenSpec validation;
- secret scanning;
- Ruff and strict mypy;
- the complete Python, contract, migration, link, and architecture suite;
- trusted-local extension conformance;
- focused D1–D5 desktop API and launcher validation;
- frontend TypeScript build and Node test suite;
- Rust formatting, unit tests, and Clippy.

The full Python suite includes focused D5 regressions for governed dataset resolution, range propagation, deterministic display downsampling, full-resolution export, saved-view persistence/schema/security, quantitative analysis, compatible/incompatible comparison behavior, and a cached 25,000-row performance case whose analytical/display path must complete within the D5 three-second budget while returning at most 240 display rows.

The frontend suite verifies typed `desktop_request` usage, absence of frontend-authored authoritative financial formulas, shared chart/volume/table presentation rows, synchronized keyboard and mouse chart inspection, readable selected-observation details, range/viewport behavior, downsampling disclosure, comparison result rendering, accessibility safeguards, reduced motion, forced colors, and 320/680 CSS-pixel responsive breakpoints.

The renderer dependency inspection confirms D5 adds no third-party chart runtime. The desktop runtime dependencies remain the existing Tauri API, React, and React DOM set; the Workbench chart is OSCA-owned SVG/DOM.

## Numerical and provenance evidence

D5 reuses the authoritative `osca.analytical_data` and `osca.quantitative_analysis` public seams rather than calculating financial series in React or Rust.

Automated evidence covers:

- canonical governed payload resolution from retained profile metadata;
- bundled offline AAPL/MSFT synthetic sample import for clean-profile compatible comparison acceptance;
- rejection of arbitrary client payload paths and metadata that escapes governed storage;
- OHLCV plus derived-series output from the same analytical result used by the chart/table surface;
- Python-authoritative RSI, ATR, Bollinger, MACD, summary statistics, exact-timestamp aligned returns, correlation, and beta;
- explicit asset-class/currency comparison incompatibility before dataset joining;
- deterministic bounded display output with first/last boundary preservation;
- full-resolution CSV plus JSON reproduction metadata independent of display downsampling;
- payload/input/output digests and point-in-time-safety evidence where supplied by the authoritative capability.

## Persistence and ownership evidence

Saved Workbench views are profile-scoped declarative records in a dedicated desktop SQLite store. Tests cover create/list/get/update/rename/delete, restart persistence, unique names, bounded JSON configuration, forbidden secret/query/broker/order fields, newer-schema rejection, and profile isolation.

D5 mutating desktop methods are classified by the Rust broker under the existing window/profile lease. Python retains the bounded profile mutation lock. Automated tests verify that the D5 saved-view/export mutations use the same opened-profile ownership boundary established in D4.

## Accessibility and interaction evidence

The Workbench provides:

- an accessible synchronized table sourced from the same returned rows as the price and volume panes;
- a focusable price chart with Left/Right Arrow and Home/End observation inspection;
- mouse-selectable chart observations through explicit candle hit targets;
- an inspection marker and live selected-observation panel with OHLCV/derived values synchronized to the selected table row;
- visible focus styling;
- screen-reader chart/volume summaries;
- non-color direction/state cues where practical;
- reduced-motion and forced-colors handling;
- responsive layouts at the required narrow/intermediate widths.

Supported-platform VoiceOver/Orca, keyboard behavior, mouse chart selection, and selected-observation readability passed manual acceptance.

## Offline, packaging, and performance disposition

Automated source/boundary tests prove the D5 Workbench does not add browser `fetch`, WebSocket, provider URL, shell, recommendation, brokerage, or order paths. D5 service results explicitly retain network/recommendation/broker/real-capital-disabled semantics. Actual no-network observation remains part of manual acceptance.

The existing native packaging contract is unchanged by D5: macOS builds the `.app` bundle and Linux builds the Debian package, both with the self-contained packaged sidecar established in D4. The exact D5 native package and responsiveness are intentionally revalidated in the supported-platform manual procedure rather than inferred from source tests.

## Defects found and resolved during D5 validation

Validation identified and resolved:

1. D5 mutating methods initially needed explicit Rust broker ownership classification;
2. the initial Workbench exposed synchronized table values but lacked direct keyboard-selectable chart observation inspection;
3. an incompatible comparison could attempt governed dataset resolution before reporting semantic incompatibility;
4. new test files exposed Ruff import-layout failures before deeper validation could run;
5. a saved-view test fixture initially created a nested profile path incorrectly;
6. a frontend range-client edit briefly diverged from the shared typed range-object contract;
7. an initial responsive test asserted CSS formatting rather than the semantic breakpoint;
8. the clean-profile offline acceptance path initially imported only AAPL, leaving no bundled compatible comparison dataset for the default MSFT comparison.

All listed defects are corrected on the validated candidate.

## macOS ARM64 manual acceptance

**Result: PASS.**

The complete clean-profile D5 procedure passed on macOS ARM64, including packaged/native launch, offline Workbench sample and retained-data paths, governed series/range interaction, chart/table parity, keyboard and mouse chart observation inspection, readable selected-observation evidence, indicators, compatible and incompatible comparisons, downsampling disclosure, full-resolution CSV/metadata export, saved-view lifecycle and isolation, accessibility/responsive behavior, and typical cached/local responsiveness.

## Linux x86-64 manual acceptance

**Result: PASS.**

The complete clean-profile D5 procedure passed on Linux x86-64, including packaged/native launch, offline Workbench sample and retained-data paths, governed series/range interaction, chart/table parity, keyboard and mouse chart observation inspection, readable selected-observation evidence, indicators, compatible and incompatible comparisons, downsampling disclosure, full-resolution CSV/metadata export, saved-view lifecycle and isolation, accessibility/responsive behavior, and typical cached/local responsiveness.

Private host paths, credentials, provider account information, and machine-local profile identifiers must not be committed.

## Current disposition

- Implementation slices: complete.
- Automated validation: pass on `12724813d1a542663a5fbdd8649754107a8f3357`.
- Numerical-authority and narrow-desktop-boundary checks: pass.
- Automated performance and dependency/license checks: pass.
- macOS ARM64 manual acceptance: pass.
- Linux x86-64 manual acceptance: pass.
- D5 exit decision: pass; merge remains subject to explicit repository-owner direction.
