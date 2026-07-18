# Model Seam

- **Status:** Draft
- **Owner:** ML lifecycle capability
- **Purpose:** Standardize experiment, training, evaluation, registry, inference, deployment, and monitoring contracts while allowing replaceable model implementations.

## Contract groups

- feature and label contracts with information-availability semantics;
- experiment and training definitions;
- training-run record and produced artifacts;
- evaluation request and task-specific metrics;
- immutable model-version manifest;
- deployment pointer and champion/challenger policy;
- inference request and prediction result;
- drift and outcome-monitoring records.

## Mandatory behavior

- Model versions are immutable and identified by manifest and integrity digest.
- Training records pin dataset revisions, feature definitions, splits, code, dependencies, parameters, seeds, and material hardware context.
- Final held-out data is protected from repeated selection use.
- Simple baselines and non-ML alternatives are retained in evaluation evidence.
- Inference records model version, feature data, effective time, calibration, uncertainty, and provenance.
- Deployment changes do not rewrite historical decisions.
- Retraining never implies automatic promotion.
- Imported unsafe serialization formats may be rejected or quarantined.
- Deterministic risk remains external authority, including for reinforcement learning.

## Conformance evidence

Fixtures cover leakage detection, reproducible training identity, invalid splits, baseline comparison, model integrity, incompatible feature schema, deterministic inference where claimed, calibration output, rollback, and monitoring gaps.