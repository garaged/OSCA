# Design — M4 research projects, analytics, and visualization

## Approach

M4 adds additive contracts under a new research/analysis capability area. The contracts reference governed dataset and temporal identities from M2/M3 rather than reading persistence internals.

## Boundaries

- Project records own research intent, selected dependencies, and timeline evidence.
- Hypothesis records own assumptions, expected outcomes, invalidation conditions, confidence, and lifecycle state.
- Analysis graph records own dependency structure, input references, output declarations, quality policy, and interval requirements.
- Analytical output records own typed result identity and provenance.
- Visualization specifications consume analytical output identities only.
- Dashboard specifications compose governed visualization identities without mutating underlying analyses or outputs.

## Compatibility

M4 does not change M2/M3 market-data contracts. External packaging and runtime isolation remain deferred to M5.
