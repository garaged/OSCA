# D10 Specification — ML Data Platform, Feature Catalog, and Experiment UX

## Authority and boundary

D10 implements REQ-0415 through REQ-0421. It consumes only governed retained OHLCV revisions through desktop API resolution. It produces reproducible research evidence, never model approval, recommendations, or execution authority.

## Dataset and feature lineage

Each run records dataset revision ID, payload digest, symbol/timeframe, feature definitions, label horizon, split policy, parameters, code revision, and output digest. Feature rows use only information available at their timestamp; labels occur strictly after the feature timestamp.

The initial catalog contains three built-in completed-bar return features: last return, rolling mean return, and rolling return volatility. Their identities and versions are stable, their transformation and lookback semantics are visible, and missing inputs fail closed. Regression uses a future-return label; classification uses a future-direction label. Arbitrary feature code and partial reinterpretation of the bounded trainer are excluded.

Dataset construction is server-authoritative. The renderer supplies a canonical asset and timeframe, never a payload path. Planning resolves one immutable retained revision and records its payload SHA-256, source attribution, row count, effective end, and data policies. Execution re-resolves and verifies the pinned revision and digest before computation.

## Validation

Chronological train/validation/test partitions are mandatory. The label horizon is purged before partition boundaries, and configured embargo removes additional rows. Scaling fits training rows only. Test metrics are retained but are not a model-approval signal. A persistence or moving-average baseline is mandatory.

The initial data policies are explicit: survivorship uses a single-asset experiment without universe-selection inference; corporate actions preserve the governed dataset's declared semantics; and missing data fails closed rather than being imputed or silently dropped.

## Lifecycle and persistence

Experiment definitions are immutable retained records. Lifecycle states are planned, running, completed, review-required, failed, and cancelled. Planning is separate from execution so a user can inspect or cancel retained intent before compute begins. Interrupted running records recover as failed with a diagnostic and may be deliberately rerun. Timeline events and result/output digests survive restart.

D10 owns a profile-scoped versioned SQLite store. Newer schemas fail closed. Mutations require the established Rust profile ownership lease and Python mutation lock. Reads do not acquire mutation authority.

## Desktop application API and UX

The method family is `ml.catalog.list`, `ml.experiment.create`, `ml.experiment.run`, `ml.experiment.list`, `ml.experiment.get`, and `ml.experiment.cancel`. Results are typed and contain no client-usable filesystem path. D6 may pin an `ml_experiment` identity without embedding its dataset.

ML Lab exposes the feature catalog, dataset/policy configuration, bounded model settings, retained registry, lifecycle actions, chronological split ranges, model-versus-baseline metrics, findings, lineage, and digests. Keyboard focus, narrow-width layouts, reduced motion, forced colors, empty/error/loading states, and non-color status meaning are required.

## Bounds and failure

All horizons, windows, embargoes, iterations, and row counts are bounded. Invalid splits, insufficient data, non-governed input, or unsafe feature/label declarations fail closed with actionable feedback. D10 has no network, credential, automatic promotion, recommendation, broker, or real-capital behavior.

## Exit criteria

REQ-0415 through REQ-0421 must map to executable implementation and tests. Python, frontend, Rust, persistence/recovery, architecture, links, secrets, and strict OpenSpec gates must pass. The deterministic acceptance profile must retain sufficient D10 data, one completed experiment, baseline evidence, and a typed D6 project pin. Human acceptance is limited to changed-surface usability, evidence readability, accessibility, and safety-boundary judgment on macOS ARM64 and Linux x86-64.
