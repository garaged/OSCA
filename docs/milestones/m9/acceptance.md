# M9 Acceptance Criteria

| ID | Criterion | Verification |
|---|---|---|
| M9-AC-001 | Feature definitions preserve identity, source dataset, transformation, value type, and point-in-time safety. | Unit tests, inspection |
| M9-AC-002 | Label definitions preserve objective, horizon, source dataset, and leakage-check status. | Unit tests, inspection |
| M9-AC-003 | Training workflows preserve trainer, feature set, label, split policy, and parameter set identity. | Unit tests |
| M9-AC-004 | Model artifacts preserve immutable artifact identity, URI, digest, model family, and lifecycle status. | Unit tests |
| M9-AC-005 | Evaluation reports require holdout metrics and calibration methodology. | Unit tests |
| M9-AC-006 | ML promotion decisions fail closed when findings contain errors or thresholds are not met. | Unit tests |
| M9-AC-007 | Manual testing and usage documentation is reviewed and updated for M9. | Documentation inspection |
