# U10 — Research-Evidence Workspace

- **Status:** In implementation
- **Baseline:** U9 merged through PR #72 at `80822eea84094d34123e2eaa6aa28cb9b7c7d2d9`
- **Branch:** `agent/u10-research-evidence-workspace`

## Intent

Make the analyst workspace represent the complete retained research workflow instead of exposing model artifacts as generic reports.

## Required outcome

A retained U9/U8 workflow is navigable from dataset acquisition through experiment, diagnostic, optional validation, and pipeline-run evidence. Every view remains read-only and preserves provider, licensing, recommendation, promotion, broker, autonomous-execution, and real-capital boundaries.

## Implementation sequence

1. Dedicated workspace sections for acquisitions, experiments, diagnostics, validations, and pipeline runs.
2. Read-only item detail contracts and endpoints with raw evidence, digests, assumptions, warnings, reviewer/rationale, and safety states.
3. Upstream/downstream lineage resolution and explicit incomplete, corrupt, incompatible, and orphaned states.
4. Date, symbol, timeframe, type, and status filtering.
5. Raw JSON download and portable evidence-bundle export consistent with provider policy.
6. Dynamic-port startup plus CLI/API/export equivalence tests.
7. Clean-profile manual acceptance using the retained U9 evidence chain.

## Acceptance gates

- Dedicated sections do not duplicate their artifacts under generic reports.
- The U9 dataset, acquisition, U8 manifest, experiment, and diagnostic form one navigable lineage.
- Validation is shown only when present and is explicitly not expected for diagnostic-ineligible runs.
- Missing, malformed, incompatible, and orphaned evidence never appears as healthy.
- Exports exclude secrets and obey provider redistribution policy.
- Workspace remains loopback-only, read-only, network-disabled, recommendation-disabled, broker-disabled, and real-capital-disabled.
- Hosted Ruff, strict mypy, pytest, OpenSpec, document-link, architecture, and secret-scan checks pass.

## Non-goals

U10 does not enable recommendations, automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote write APIs, or public evidence sharing.
