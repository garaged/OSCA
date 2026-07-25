# M4 Intent — Research Projects, Analytics, and Visualization

- **Status:** Draft
- **Governing role:** Product authority
- **Architecture, data, quality, and extension approval:** Pending for M4 implementation entry
- **Purpose:** Enable a local owner to complete a governed exploratory research project using explicit project intent, analytical outputs, analysis graphs, visualization specifications, and retained evidence.
- **Authoritative sources:** PRD sections 11, 15, 18-21, 34-39; D-009, D-019, D-021-D-026, D-046
- **Baseline:** Completed M3 multi-timeframe temporal correctness
- **Review trigger:** project identity, artifact lineage, analytical-output taxonomy, extension contract, visualization grammar, export semantics, or provider-production change
- **Last reviewed:** 2026-07-24

## Intent statement

Enable a local owner to frame a research project, declare hypotheses and data requirements, compose deterministic analysis graphs over governed datasets, produce structured observations/signals/findings, render declarative visualization specifications, and preserve enough provenance to promote ad hoc exploration into a reproducible project.

## User outcome

A user can create a project with a stated research objective, attach hypotheses, run an inspectable analysis graph, review structured analytical outputs and visualization specifications, and retain a project timeline that explains the evidence and dependencies behind the exploration.

## In scope

- project, timeline, hypothesis, branch, and decision primitives;
- global catalog references needed by project records;
- structured analytical output primitives for observations, signals, findings, theses, and reports;
- declarative analysis graph contracts with typed nodes, inputs, outputs, dependencies, and data-quality requirements;
- declarative visualization specification primitives for charts, tables, dashboards, provenance disclosure, and export metadata;
- ad hoc workspace promotion into governed project records;
- tests, documentation, OpenSpec, traceability, and evidence for the first governed research-project slice.

## Non-goals

- independently packaged external extensions;
- full web dashboard implementation;
- ML training, backtesting, paper trading, live execution, or LLM orchestration;
- production promotion for paid/authenticated provider access;
- arbitrary frontend code execution or direct database access from analyses.
