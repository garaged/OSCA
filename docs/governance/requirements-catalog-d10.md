# D10 Requirements Catalog — ML Data Platform, Feature Catalog, and Experiment UX

- **Milestone:** D10
- **Status:** Active implementation
- **Baseline:** Accepted D9 / PR #89
- **Authority:** Product requirements sections 9, 11, 13, 15-18; ADR-0005; ADR-0009; ADR-0035; D10 intent

| ID | Requirement | Verification |
|---|---|---|
| REQ-0415 | D10 SHALL build experiments only from retained, immutable governed dataset revisions; a client path or mutable latest-data reference SHALL be rejected. | Integration and boundary tests |
| REQ-0416 | D10 SHALL retain versioned feature and label definitions with explicit point-in-time and leakage declarations. | Contract and persistence tests |
| REQ-0417 | D10 SHALL use chronological train/validation/test splits and purge label horizons; embargo is explicit and bounded. | Split golden tests |
| REQ-0418 | D10 SHALL fit transforms and models using training data only, and SHALL retain data, feature, split, code, parameter, and digest lineage. | Leakage and reproducibility tests |
| REQ-0419 | D10 SHALL require a simple baseline and show baseline comparison alongside validation and test evidence. | Service and desktop tests |
| REQ-0420 | D10 SHALL bound local experiment resources, provide retained status/cancellation semantics, and fail closed on invalid configuration. | Negative and lifecycle tests |
| REQ-0421 | D10 SHALL remain offline-capable research evidence: no automatic promotion, recommendation, broker execution, credentials, or live-capital path. | Source boundary tests |
