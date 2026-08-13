# D5 Production Charting and Quantitative Analysis Workbench

- **Status:** Implementation and automated validation complete; supported-platform manual acceptance pending
- **Baseline:** D4 merge `a4e733292ff42775848520afd536d57a18cada1f`
- **Branch:** `agent/d5-charting-quant-workbench`
- **Intent:** `intent.md`
- **Specification:** `specification.md`
- **Requirements:** `../../governance/requirements-catalog-d5.md`
- **Traceability:** `traceability.md`
- **Manual acceptance:** `manual-acceptance.md`
- **Validation evidence:** `validation-evidence.md`
- **Exit review:** `exit-review.md`
- **OpenSpec:** `../../../openspec/changes/d5-charting-quant-workbench/`

## Outcome

D5 turns OSCA's existing governed analytical and quantitative capabilities into a first-class desktop workbench for local time-series inspection, deterministic indicators, compatible comparisons, synchronized chart/table inspection, declared downsampling, full-resolution evidence export, and profile-scoped saved views.

## Architecture direction

- Python remains authoritative for numerical series, indicators, comparison semantics, downsampling, export data, validation, and saved-view persistence.
- React renders typed returned values and captures declarative user intent plus presentation-only viewport/inspection state.
- Rust remains the existing transport/session broker and only classifies D5 profile mutations under the established ownership lease.
- D5 uses an OSCA-owned declarative SVG/DOM renderer and adds no third-party chart runtime dependency.
- Existing `osca.analytical_data` and `osca.quantitative_analysis` public seams are reused instead of duplicating calculations.
- Local/sample/cached data remains usable without paid providers or network access.

## Delivered slices

1. D5 requirements, specification, OpenSpec, traceability, and manual-acceptance baseline.
2. Typed authoritative D5 desktop series, quantitative analysis, comparison, and full-resolution export APIs.
3. Desktop price/volume chart, synchronized table, explicit row/downsampling evidence, and presentation zoom/pan.
4. Deterministic indicator and compatible comparison controls.
5. Profile-scoped saved views with schema/version, security validation, persistence, and ownership locking.
6. Keyboard-selectable synchronized chart inspection with matching table-row state.
7. Automated performance, dependency/license, boundary, accessibility-source, and supported desktop CI evidence.

## Remaining exit work

The complete clean-profile manual procedure must pass on both supported D5 platforms:

- macOS ARM64;
- Linux x86-64.

After both passes, validation evidence and the provisional exit review must be reconciled, final hosted CI must pass on that evidence head, and PR #85 requires explicit repository-owner direction before **Squash and merge**.

D5 does not add recommendations, model training, strategy execution, brokerage connectivity, or real-capital execution.
