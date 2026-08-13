# D5 Exit Review — Production Charting and Quantitative Analysis Workbench

- **Status:** Provisional — implementation and automated validation pass; supported-platform manual acceptance pending
- **Pull request:** #85
- **Baseline:** D4 merge `a4e733292ff42775848520afd536d57a18cada1f`
- **Validated implementation candidate:** `02b8c58aa706fa857e8b0abbfa440b5e6c65455c`

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

Disposition: implementation pass; final requirement closure awaits manual evidence for the explicitly manual obligations.

## Automated validation disposition

Quality `31689929269` (#1091) and Desktop Foundation `31689929139` (#238) passed on implementation candidate `02b8c58aa706fa857e8b0abbfa440b5e6c65455c`.

Passing gates include strict OpenSpec, secret scanning, Ruff, strict mypy, the complete Python/contracts/migrations/links/architecture suite, trusted-local extension conformance, desktop API/launcher validation, frontend build/tests, Rust format/tests/Clippy, large-series bounded-performance regression, and renderer dependency/license inspection.

The D5 frontend now includes keyboard-selectable synchronized chart inspection using Left/Right Arrow and Home/End, with an explicit marker, live OHLCV/derived-value description, and matching selected table row.

Disposition: pass.

## Performance and dependency disposition

The cached-series regression exercises 25,000 retained OHLCV rows with SMA and EMA and requires authoritative series generation plus deterministic downsampling to 240 display rows in under three seconds, preserving first/last boundaries. This gate passes in the hosted suite.

D5 introduces no third-party chart runtime. Existing Tauri/React dependencies remain the runtime set for the renderer surface.

Disposition: automated performance/dependency pass; packaged acceptance-hardware responsiveness remains pending manual validation.

## Persistence and safety disposition

Saved views support create/list/get/update/rename/delete with unique normalized names, optional descriptions, bounded declarative JSON configuration, restart persistence, profile isolation, schema-version rejection, and forbidden executable/query/secret/provider/broker/order fields.

D5 mutations use the established desktop window/profile lease plus Python profile mutation locking. Comparison compatibility is validated before joining datasets, and incompatible asset-class/currency semantics fail visibly.

Disposition: automated pass; concurrent-owner and restart behavior remain part of manual acceptance.

## Supported-platform manual acceptance

- macOS ARM64: PENDING.
- Linux x86-64: PENDING.

The complete clean-profile procedure in `manual-acceptance.md` must pass on both platforms. Required evidence includes packaged launch, offline network observation, keyboard chart/table parity, deterministic indicators and invalid-parameter handling, compatible/incompatible comparisons, downsampling disclosure, full-resolution export, saved-view restart/profile isolation/ownership, VoiceOver or Orca, high contrast/forced colors, reduced motion, 320/680/desktop layouts, and packaged responsiveness.

Disposition: blocking until both platform runs pass.

## Exit decision

D5 implementation and automated-validation gates are satisfied. The milestone is **not merge-ready yet** because supported-platform manual acceptance is an explicit exit criterion.

**D5 exit decision: PENDING MANUAL ACCEPTANCE.**

After both platform runs pass, reconcile this review and `validation-evidence.md`, run final hosted CI on the evidence head, mark PR #85 ready, and obtain explicit repository-owner direction before using **Squash and merge**.
