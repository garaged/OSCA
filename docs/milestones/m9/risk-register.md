# M9 Risk Register

| Risk | Treatment |
|---|---|
| Look-ahead leakage in features or labels | Require point-in-time feature declarations and leakage-checked labels. |
| Overfitting or weak evaluation | Require holdout metrics and calibration methodology before promotion. |
| Unsafe automatic promotion | Keep retraining and paper challenger promotion explicit and non-automatic. |
| Artifact tampering or ambiguity | Require immutable artifact identities and digest prefixes. |
| Confusion with live trading | Keep live execution explicitly deferred in docs and tests. |
