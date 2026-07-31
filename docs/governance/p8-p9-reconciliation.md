# P8-P9 Requirements and Traceability Reconciliation

- **Status:** Active milestone reconciliation
- **Governing roles:** Product authority and quality authority
- **Reviewed:** 2026-07-31
- **Purpose:** Reconcile P8 completion evidence and the corrected P9 implementation scope without rewriting historical requirement or traceability records for earlier milestones.
- **Related pull request:** #52

## Authority

This record supplies the current status and evidence links for REQ-0212 through REQ-0225. It is read together with the requirements catalog and traceability register. Where those append-only indexes still show a pre-validation P8 or pre-terms-review P9 status, this reviewed reconciliation is the current milestone evidence until the indexes are compacted in a later documentation-only maintenance pass.

The approved PRD, decision log, D-040 licensing policy, ADR-0043 milestone sequence, accepted milestone specifications, and OpenSpec specifications remain authoritative.

## P8 completion reconciliation

| Requirements | Current status | Implementation and verification evidence | Documentation and retained evidence | Deferred boundaries |
|---|---|---|---|---|
| REQ-0212-REQ-0218 | Verified | `src/osca/backtest_paper/*`; `src/osca/bootstrap/cli.py`; `tests/test_p8_backtest_paper_happy_path.py`; PR #44; successful compatibility and documentation follow-ups #45-#51 | [P8 milestone](../milestones/p8/README.md); [P8 exit review](../milestones/p8/exit-review.md); [manual workflow](../milestones/p8/user-testing-quickstart.md); [retained manual evidence](../../evidence/p8/manual-backtest-paper-report.md); [manual testing](../testing/manual-testing.md) | Live providers, live paper brokers, credential materialization, runtime routing, production ingestion, recommendations, autonomous execution, and real-capital orders remain disabled. |

### P8 manual evidence

The successful macOS Apple Silicon/Python 3.13 run imported `tests/fixtures/local_ohlcv/aapl_backtest_daily.csv` with `row_count: 10`, processed ten AAPL daily bars, generated three simulated evidence trades, and retained paper run `aaad0f77-aebd-455b-832a-9df9feafb680` in `local-evidence-only` mode.

### P8 Quality evidence

- PR #44: P8 implementation hosted Quality passed.
- PR #45: run `30594286817`.
- PR #46: run `30594598842`.
- PR #47: run `30595013370`.
- PR #48: run `30595313371`.
- PR #49: run `30595759235`.
- PR #50: run `30596825840`.
- PR #51: run `30600239512`.

## P9 corrected requirement interpretation

The immutable IDs REQ-0219 through REQ-0225 remain allocated to P9. Their current reviewed interpretation is:

| Requirement | Corrected implementation meaning | Current status | Verification |
|---|---|---|---|
| REQ-0219 | Deliver an opt-in SEC EDGAR enrichment preview and a fail-closed FRED terms gate. | Implementation candidate | P9 contracts, services, CLI, tests, specification, and OpenSpec. |
| REQ-0220 | Analysts can replay SEC fixtures and explicitly retrieve bounded SEC company-facts or submissions evidence; FRED attempts return a structured policy block. | Implementation candidate | Module CLI tests and manual quickstart. |
| REQ-0221 | Implement SEC fixture replay, explicit live opt-in, user-agent validation, approved HTTPS paths, fair-access throttling, bounded responses, local SEC cache/provenance, and FRED policy blocking. | Implementation candidate | `src/osca/provider_preview/*`; provider catalog/adapter updates; focused tests. |
| REQ-0222 | Fail closed for missing opt-in, invalid identity, provider errors, malformed or oversized payloads, embedded secret values, FRED live use, and all deferred production/trading behavior. | Implementation candidate | Negative tests and evidence flags. |
| REQ-0223 | Pass Ruff, strict mypy, pytest/contracts/migrations/links/architecture, OpenSpec, secret scanning, and hosted Quality before completion. | Pending hosted Quality | PR #52 workflow evidence. |
| REQ-0224 | Publish executable manual instructions for SEC fixture replay, optional SEC live preview, cache inspection, and the FRED policy block. | Implementation candidate | [P9 user testing quickstart](../milestones/p9/user-testing-quickstart.md). |
| REQ-0225 | Record implemented SEC behavior, fixture-backed contracts, FRED policy-blocked behavior, validation, and residual deferrals in the exit review. | Implementation candidate | [P9 exit review](../milestones/p9/exit-review.md). |

## P9 trace links

| Requirements | Authority | Milestone | Specification | Code | Tests | Documentation | Status |
|---|---|---|---|---|---|---|---|
| REQ-0219-REQ-0225 | D-040; ADR-0043; approved P9 scope correction on 2026-07-31 | [P9 milestone](../milestones/p9/README.md) | [P9 specification](../specifications/p9-sec-fred-live-preview-adapters.md); [OpenSpec](../../openspec/specs/p9-sec-fred-live-preview-adapters/spec.md) | `src/osca/provider_preview/*`; `src/osca/provider_catalog/services.py`; `src/osca/provider_adapters/services.py` | `tests/test_p9_sec_preview_fred_terms_gate.py`; `tests/test_provider_catalog.py`; `tests/test_provider_adapters.py`; deterministic SEC fixture | [P9 quickstart](../milestones/p9/user-testing-quickstart.md); [P9 exit review](../milestones/p9/exit-review.md); [manual testing](../testing/manual-testing.md) | Implementation candidate pending hosted Quality and PR review |

## Terms and licensing disposition

- SEC EDGAR live preview is implemented only through explicit opt-in, a declared organization/contact user agent, approved `data.sec.gov` HTTPS paths, conservative throttling, bounded responses, and evidence-only semantics.
- FRED remains a preferred official macro candidate but its live implementation readiness is `NEEDS_EVIDENCE`.
- The FRED fixture contract remains available for deterministic conformance tests.
- P9 performs no FRED network request, resolves no FRED secret reference, and stores no FRED API content.

## Remaining roadmap assessment

- P10 remains responsible for governed runtime routing and explicit local, fixture, live-preview, stale, unavailable, and policy-blocked source states.
- P11 remains responsible for a practical analyst workspace over datasets, reports, backtests, and enrichment evidence.
- P12 model-assisted previews are optional and must remain budgeted, provenance-rich, and fail closed.
- P13-P15 production/provider/operations work remains gated by exact licensing, quota, credential, retention, export, redistribution, and security evidence.
- P16-P17 real-money work remains deferred behind an explicit go/no-go decision and is not authorized by P9.
