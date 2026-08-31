# D10 Traceability — ML Data Platform, Feature Catalog, and Experiment UX

| Authority / requirement | Implemented evidence |
|---|---|
| ADR-0035 | Existing `osca.ml` lifecycle contracts remain separate from D10 experiment execution; D10 results cannot create promotion decisions. |
| ADR-0009 | `desktop_api.ml_lab` owns its versioned profile store and consumes D5 data only through `resolve_governed_dataset`; D6 receives typed pin identities only. |
| REQ-0415 | Server-side governed resolver, pinned revision and payload SHA-256, execution-time identity/integrity check, and arbitrary-path rejection in `test_d10_desktop_ml_lab.py`. |
| REQ-0416 | Versioned built-in feature/label rows, point-in-time/lookback/missing-data/leakage metadata, immutable definition snapshots, catalog API, and ML Lab catalog. |
| REQ-0417 | `ml_experiments.engine` chronological splits, horizon purge, explicit embargo, and retained partition ranges; U5 and D10 tests. |
| REQ-0418 | Training-only scaler, deterministic input/output digests, pinned request/policy/resource lineage, restart persistence tests. |
| REQ-0419 | Mandatory persistence/moving-average baseline metrics and ML Lab model-versus-baseline table. |
| REQ-0420 | Bounded Pydantic request, D10 10,000-iteration cap, planned/run/cancel/fail lifecycle, interruption recovery, newer-schema rejection, Rust mutation classification. |
| REQ-0421 | Safety flags and source tests prove no renderer filesystem/network authority, credentials, automatic promotion, recommendations, broker submission, or real-capital execution. |

## Validation locations

- Python: `tests/test_d10_desktop_ml_lab.py`, `tests/test_u5_ml_experiments.py`.
- Frontend: `apps/desktop/tests/ml-lab.test.mjs` plus TypeScript build.
- Rust: `d10_ml_writes_require_profile_ownership` in `apps/desktop/src-tauri/src/lib.rs`.
- Acceptance: `scripts/prepare_desktop_acceptance.py` retains 220-row paired samples, one completed D10 experiment, baseline evidence, and a D6 ML pin.
- OpenSpec: `openspec/changes/d10-ml-data-platform`.
