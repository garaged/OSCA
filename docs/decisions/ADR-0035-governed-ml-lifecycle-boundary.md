# ADR-0035 - Governed ML Lifecycle Boundary

- **Status:** Draft
- **Date:** 2026-07-25
- **Milestone:** M9
- **Deciders:** Architecture authority, product authority, quality authority

## Context

OSCA now has governed market data, research, backtesting, event-driven validation, and paper-evaluation foundations. ML can add predictive power, but only if model artifacts and promotion decisions remain traceable and cannot bypass deterministic validation.

## Decision

M9 introduces a separate `osca.ml` capability for ML lifecycle contracts and deterministic promotion gates.

Feature definitions, label definitions, training workflows, experiment runs, model artifacts, evaluation reports, and promotion decisions are durable evidence records. ML promotion may approve a model artifact for F2 event-driven validation only after explicit evaluation evidence. Paper challenger deployment remains a later explicit decision and cannot be implied by model training or retraining.

## Consequences

- ML lifecycle records are governed separately from backtesting and paper evaluation.
- Point-in-time safety, leakage checks, holdout metrics, calibration methodology, and artifact digests are required before promotion.
- Retraining creates evidence but does not automatically promote a model.
- Live execution remains out of scope.
