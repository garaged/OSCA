# Analysis Seam

- **Status:** Draft
- **Owner:** Analytical composition capability
- **Purpose:** Execute built-in and extension-provided analytical methods through inspectable, reproducible dependency graphs.

## Contract groups

- **Capability descriptor:** identity, category, supported instruments and intervals, input and parameter schemas, lookback, warm-up, quality requirements, provisional-data behavior, determinism, resource expectations, and methodology references.
- **Analysis definition:** immutable versioned graph of capability nodes, parameters, dependencies, provider and freshness policies, and output declarations.
- **Execution request:** project context, dataset references, effective time, budget, seed, cancellation, required completion, and permission context.
- **Result:** typed observations, signals, findings, theses, recommendations, diagnostics, visualization references, provenance, quality, confidence, lifecycle, and reproducibility status.

## Mandatory behavior

- Inputs use governed dataset or artifact references, not private storage locations.
- Every durable run records exact graph, capability versions, parameters, datasets, code or build identity, environment, seed, and timing assumptions.
- Independent graph nodes may run concurrently only when dependency and consistency semantics allow it.
- Cache reuse requires an identity derived from all material inputs and policy context.
- Partial or degraded outputs are explicitly typed and cannot masquerade as complete results.
- LLM narrative may accompany but cannot replace deterministically calculated values and evidence.

## Conformance evidence

Tests cover deterministic replay, seed control, missing and provisional data, graph cycles, schema validation, cache identity, cancellation, resource exhaustion, partial outputs, provenance completeness, and extension failure isolation.