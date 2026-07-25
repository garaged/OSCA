# M9 Governed ML Lifecycle Specification

- **Status:** Draft
- **Milestone:** M9
- **Requirements:** REQ-0113-REQ-0119
- **ADR:** ADR-0035
- **Manual testing:** M9 updates `docs/testing/manual-testing.md`

## Requirements

### Feature registry

ML feature definitions must preserve stable identity, value type, source dataset, transformation description, creation time, and point-in-time safety.

### Label registry

ML label definitions must preserve stable identity, objective, horizon, source dataset, creation time, and leakage-check evidence.

### Training workflow metadata

Training workflows must preserve trainer identity, feature set, label identity, split policy, parameter-set identity, and creation time.

### Experiment and model registry

Experiment runs and model artifacts must preserve immutable identities, dataset revision, code revision, artifact URI, artifact digest, model family, and lifecycle status.

### Evaluation and calibration

Evaluation reports must preserve metrics by dataset split and require holdout metrics plus calibration methodology.

### Promotion gate

ML promotion decisions must fail closed when quality findings contain errors or when required holdout thresholds are not met.

### Event validation and paper challenger integration

ML model artifacts must require approved ML promotion before F2 event-validation linking. Paper deployment decisions must preserve account, run, role, promotion decision, rationale, findings, and approval state.

### Drift, outcome, and retraining monitoring

ML monitoring reports must preserve drift metrics, outcome metrics, status, findings, and observation time. Retraining records must preserve source model, trigger, workflow, rationale, and requested time without automatic promotion.

### Metadata persistence

ML lifecycle metadata must persist stable records and support workflow, experiment, and model-artifact scoped queries without executing training.

### Manual testing

M9 must review and update the manual testing and usage baseline for ML lifecycle operator-visible behavior.
