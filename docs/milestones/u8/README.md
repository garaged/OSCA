# U8 Real-World Workflow Reconciliation

## Intent

Convert the August 1, 2026 end-to-end AAPL exercise into a repeatable, operator-visible workflow before adding more research capabilities.

## This change

- adds one guided `osca-research-pipeline` command for U5 experiment, U6 diagnostic, and human-gated U7 validation
- requires an explicit approval flag, reviewer, and rationale before U7
- retains experiment, diagnostic, request, result, and manifest evidence under the configured storage root
- makes those artifacts discoverable by the existing recursive analyst-workspace scan
- records deterministic provenance, summary metrics, evidence digest, and all deferred safety boundaries in the manifest
- fails closed when U6 does not return `eligible_for_f2_validation`
- adds regression coverage for the approval gate and retained-evidence layout
- adds the official real-world quickstart and first retained baseline interpretation

## Follow-up reconciliation

The remaining usability work should stay ahead of new analytical milestones:

1. Fold the guided workflow into the primary `osca` Typer command surface while preserving the standalone entry point for compatibility.
2. Add first-class primary CLI commands for analytical data, quantitative analysis, ML experiments, prediction diagnostics, validation, and analyst workspace startup.
3. Render accepted enum values in help output.
4. Add governed free historical-data acquisition only after source attribution, terms, schema, quota, and retention behavior are documented and tested.
5. Add dedicated workspace sections and detail views for ML experiments, diagnostics, and model validations instead of presenting them as generic report artifacts.
6. Update `docs/testing/manual-testing.md` through U8 and keep it current for every operator-visible milestone.
7. Add dynamic-port workspace startup and CLI/API equivalence to hosted regression coverage.

## Safety

U8 remains local evidence-only. It does not authorize or implement recommendations, live model serving, automatic promotion, broker or exchange connectivity, autonomous execution, or real-capital orders.
