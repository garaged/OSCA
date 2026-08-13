# D5 Production Charting and Quantitative Analysis Workbench

- **Status:** Specification and implementation in progress
- **Baseline:** D4 merge `a4e733292ff42775848520afd536d57a18cada1f`
- **Branch:** `agent/d5-charting-quant-workbench`
- **Intent:** `intent.md`
- **Specification:** `specification.md`
- **Requirements:** `../../governance/requirements-catalog-d5.md`
- **Traceability:** `traceability.md`
- **Manual acceptance:** `manual-acceptance.md`
- **OpenSpec:** `../../../openspec/changes/d5-charting-quant-workbench/`

## Outcome

D5 turns OSCA's existing governed analytical and quantitative capabilities into a first-class desktop workbench for local time-series inspection, deterministic indicators, compatible comparisons, synchronized chart/table inspection, declared downsampling, full-resolution evidence export, and profile-scoped saved views.

## Architecture direction

- Python remains authoritative for numerical series, indicators, comparison semantics, downsampling, export data, validation, and saved-view persistence.
- React renders typed returned values and captures declarative user intent only.
- Rust remains the existing transport/session broker and gains no numerical or generic data authority.
- D5 initially uses an OSCA-owned declarative SVG/DOM renderer and adds no third-party chart runtime dependency.
- Existing `osca.analytical_data` and `osca.quantitative_analysis` public seams are reused instead of duplicating calculations.
- Local/sample/cached data remains usable without paid providers or network access.

## Delivery sequence

1. Requirements, specification, OpenSpec, and manual-acceptance baseline.
2. Typed authoritative D5 desktop series/export API and tests.
3. Desktop chart/table workbench with bounded rendering and accessibility.
4. Deterministic indicator and comparison controls.
5. Profile-scoped saved views and recovery/locking behavior.
6. Full-resolution export and reproduction metadata.
7. Performance, licensing, supported-platform manual acceptance, evidence, and exit review.

D5 does not add recommendations, model training, strategy execution, brokerage connectivity, or real-capital execution.
