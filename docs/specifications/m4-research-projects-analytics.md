# Specification — M4 Research Projects, Analytics, and Visualization

- **Status:** Draft
- **Governing role:** Architecture authority
- **Approval roles:** Product, data, quality, and extension authorities
- **Governing intent:** [M4 intent](../milestones/m4/intent.md)
- **Requirements:** REQ-0053-REQ-0068
- **Related decisions:** D-009, D-019, D-021-D-026, D-046; ADR-0001-ADR-0029
- **Risk class:** Governed product, lineage, and analysis-contract change
- **Last reviewed:** 2026-07-24

## Public contract families

- `osca.research.project` 1.0.0 — draft;
- `osca.research.hypothesis` 1.0.0 — draft;
- `osca.research.timeline-event` 1.0.0 — draft;
- `osca.analysis.graph` 1.0.0 — draft;
- `osca.analysis.output` 1.0.0 — draft;
- `osca.visualization.specification` 1.0.0 — draft;
- `osca.visualization.dashboard` 1.0.0 — draft.

## Behavioral specification

Projects identify a research objective, horizon, status, creation time, and default data requirements. Project timelines record typed events for decisions, hypotheses, data revisions, analysis graphs, output production, visualization creation, reports, and promotions.

Hypotheses retain assumptions, expected outcomes, invalidation conditions, confidence, and lifecycle state. State transitions are explicit, create timeline evidence, and cannot erase prior timeline events.

Analysis graphs declare typed nodes with stable identifiers, node kind, input references, output references, parameters, interval requirements, quality policy, and dependency edges. Validation rejects duplicate nodes, missing dependency targets, missing input references, dependency cycles, and unsupported provisional data use.

Analytical outputs distinguish observations, signals, findings, theses, recommendations, alerts, and reports. Outputs carry project identity, graph identity, producer identity, effective time, quality state, dataset revision references, parameter digest, and evidence references.

Visualization specifications reference analytical output identities rather than raw internal storage. Export metadata records format, generated time, producer, source outputs, downsampling or aggregation disclosure, and reproduction parameters.

Dashboard specifications compose panels from governed visualization specifications in the same project. Composition records panel metadata and source visualization identities without mutating the visualizations, analytical outputs, or underlying analyses.

M4 contracts are internal and draft extension-compatible. Independently packaged extensions remain M5 scope.
