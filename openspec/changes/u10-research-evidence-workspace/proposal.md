# Proposal: U10 Research-Evidence Workspace

## Why

The current analyst workspace discovers retained U8/U9 artifacts but presents experiments, diagnostics, validations, and pipeline manifests as generic reports. Operators cannot reliably understand lineage, missing stages, safety state, or artifact health.

## What changes

- Add dedicated acquisition, experiment, diagnostic, validation, and pipeline-run sections.
- Add read-only detail and lineage contracts.
- Add filtering by date, symbol, timeframe, type, and status.
- Add explicit incomplete, corrupt, incompatible, and orphaned states.
- Add raw JSON download and policy-governed portable evidence export.
- Preserve loopback-only, read-only, network-disabled, recommendation-disabled, broker-disabled, and real-capital-disabled boundaries.

## Non-goals

No recommendations, automatic promotion, live model serving, broker connectivity, autonomous execution, real-capital orders, remote writes, or public evidence sharing are authorized.

## Exit outcome

A retained U9/U8 workflow is navigable from dataset acquisition through experiment, diagnostic, optional validation, and pipeline run, and exported evidence agrees with CLI and API results.
