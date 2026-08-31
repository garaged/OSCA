# D10 Exit Review — ML Data Platform, Feature Catalog, and Experiment UX

## Decision

**PENDING — implementation is complete; hosted and supported-platform acceptance evidence is required.**

## Implementation criteria

- Versioned, point-in-time-safe built-in feature and label catalog: PASS
- Governed dataset selection with immutable revision and payload digest: PASS
- Explicit survivorship, corporate-action, and fail-closed missing-data policies: PASS
- Chronological train/validation/test split with horizon purge and embargo: PASS
- Training-only transforms and mandatory simple baselines: PASS
- Bounded retained experiment lifecycle, cancellation, failure, recovery, and audit events: PASS
- Reproducible definitions with engine/code revision and output digest: PASS
- Typed ML Lab workflow, evidence comparison, project pins, and profile ownership: PASS
- No automatic promotion, recommendation, broker, live-order, or real-capital authority: PASS

## Remaining gates

- exact-head hosted Quality and Desktop Foundation checks;
- macOS ARM64 changed-surface human acceptance;
- Linux x86-64 changed-surface human acceptance;
- documentation closeout against the accepted exact head.

See [validation evidence](validation-evidence.md) and [manual acceptance](manual-acceptance.md).
