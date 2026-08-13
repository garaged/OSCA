# D5 Exit Review — Production Charting and Quantitative Analysis Workbench

- **Status:** Accepted
- **Pull request:** #85
- **Baseline:** D4 merge `a4e733292ff42775848520afd536d57a18cada1f`
- **Validated implementation candidate:** `12724813d1a542663a5fbdd8649754107a8f3357`

## Delivered outcome

D5 turns OSCA's governed analytical and quantitative capabilities into a first-class desktop Workbench for local retained OHLCV inspection, deterministic indicators, compatible comparisons, synchronized price/volume/table inspection, explicit display downsampling, full-resolution evidence export, and profile-scoped saved views.

Python remains authoritative for dataset resolution, numerical calculations, comparison semantics, downsampling, export content, validation, and saved-view persistence. React renders typed returned values and maintains presentation-only viewport/inspection state. Rust retains the existing transport/session role and only classifies D5 profile mutations under the established window ownership lease.

The renderer is an OSCA-owned declarative SVG/DOM surface and adds no third-party chart runtime dependency.

## Requirements and architecture disposition

Requirements `REQ-0325` through `REQ-0340` are allocated across the D5 specification, implementation, OpenSpec capability, automated tests, manual-acceptance procedure, traceability, validation evidence, and this review.

Implemented architectural boundaries include:

- canonical governed analytical inputs only;
- no arbitrary client payload path, provider URL, database query, or frontend numerical authority;
- bounded deterministic display rows with explicit approximation disclosure;
- full-resolution export independent of display downsampling;
- declarative profile-scoped saved views with schema/version and security constraints;
- D4-compatible profile ownership/locking for D5 mutations;
- no recommendation, live-quote, strategy-execution, model-training, brokerage, or real-capital authority.

Disposition: pass.

## Automated validation disposition

Quality `31731274246`, Desktop Foundation `31731274364`, and the PR aggregate `31731272397` passed on implementation candidate `12724813d1a542663a5fbdd8649754107a8f3357`.

Passing gates include strict OpenSpec, secret scanning, Ruff, strict mypy, the complete Python/contracts/migrations/links/architecture suite, trusted-local extension conformance, desktop API/launcher validation, frontend build/tests, Rust format/tests/Clippy, large-series bounded-performance regression, and renderer dependency/license inspection.

The D5 frontend now includes keyboard-selectable synchronized chart inspection using Left/Right Arrow and Home/End, mouse-selectable chart observations, an explicit marker, a readable live selected-observation panel with OHLCV/derived values, and a matching selected table row.

Disposition: pass.

## Performance and dependency disposition

The cached-series regression exercises 25,000 retained OHLCV rows with SMA and EMA and requires authoritative series generation plus deterministic downsampling to 240 display rows in under three seconds, preserving first/last boundaries. This gate passes in the hosted suite.

D5 introduces no third-party chart runtime. Existing Tauri/React dependencies remain the runtime set for the renderer surface.

Disposition: pass.

## Persistence and safety disposition

Saved views support create/list/get/update/rename/delete with unique normalized names, optional descriptions, bounded declarative JSON configuration, restart persistence, profile isolation, schema-version rejection, and forbidden executable/query/secret/provider/broker/order fields.

D5 mutations use the established desktop window/profile lease plus Python profile mutation locking. Comparison compatibility is validated before joining datasets, and incompatible asset-class/currency semantics fail visibly.

Disposition: pass.

## Supported-platform manual acceptance

- macOS ARM64: PASS.
- Linux x86-64: PASS.

The complete clean-profile procedure in `manual-acceptance.md` passed on both platforms. Evidence covers packaged launch, offline network observation, keyboard and mouse chart/table parity, readable selected-observation inspection, deterministic indicators and invalid-parameter handling, compatible/incompatible comparisons, downsampling disclosure, full-resolution export, saved-view restart/profile isolation/ownership, VoiceOver or Orca, high contrast/forced colors, reduced motion, 320/680/desktop layouts, and packaged responsiveness.

Disposition: pass.

## Documentation disposition

The D5 Python desktop API modules intentionally carry milestone-qualified names such as `d3_service.py`, `d4_service.py`, and `d5_service.py` to preserve the desktop milestone layering and make the authority chain auditable. This naming is accepted for the current desktop architecture; a future consolidation may rename or flatten these modules only through a separate refactor with migration evidence.

Disposition: pass.

## Exit decision

D5 implementation, automated-validation, documentation, and supported-platform manual-acceptance gates are satisfied. PR #85 still requires explicit repository-owner direction before merge.

**D5 exit decision: ACCEPTED / MERGE READY**, subject to final hosted CI on this evidence-reconciliation head and explicit repository-owner direction before using **Squash and merge**.
