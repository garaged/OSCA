# ADR-0030 — M4 Research Project Contract Model

- **Status:** Accepted
- **Date:** 2026-07-24
- **Decision owner:** Architecture authority
- **Related requirements:** REQ-0053-REQ-0068
- **Related decisions:** D-009, D-019, D-021-D-026, D-046

## Context

M4 must let a local owner complete a governed exploratory research project without jumping ahead to M5 independent extension packaging or M6 strategy and backtesting behavior.

The research layer needs stable contracts for project intent, hypotheses, timeline evidence, analysis graphs, structured outputs, and visualization specifications. These contracts must consume governed data identities from M2/M3 and remain compatible with later extension packaging.

## Decision

M4 introduces internal, draft extension-compatible contract families under the research and analysis capability area:

- osca.research.project 1.0.0;
- osca.research.hypothesis 1.0.0;
- osca.research.timeline-event 1.0.0;
- osca.analysis.graph 1.0.0;
- osca.analysis.output 1.0.0;
- osca.visualization.specification 1.0.0.

Analysis graphs reference governed input and output identities instead of persistence internals. Analytical outputs retain project, graph, dataset revision, parameter, producer, quality, and evidence provenance. Visualization specifications consume analytical output identities and export reproduction metadata.

Independent package import, activation, trust-tier enforcement, and conformance kits remain M5 scope.

## Consequences

M4 can deliver a complete governed exploratory project while avoiding premature runtime packaging. Later M5 extension SDK work can formalize package boundaries around these contracts without changing their research semantics.

The cost is that M4 built-in analyses remain internal. External developers cannot yet distribute independent capabilities until M5 accepts the packaging and trust model.
