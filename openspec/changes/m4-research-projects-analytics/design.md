# Design — M4 research projects, analytics, and visualization

## Approach

M4 adds additive contracts under a new research/analysis capability area. The contracts reference governed dataset and temporal identities from M2/M3 rather than reading persistence internals.

## Boundaries

- Project records own research intent and timeline evidence.
- Analysis graph records own dependency structure and output declarations.
- Analytical output records own typed result identity and provenance.
- Visualization specifications consume analytical output identities only.

## Compatibility

M4 does not change M2/M3 market-data contracts. External packaging and runtime isolation remain deferred to M5.
