# Design: M9 Governed ML Lifecycle

## Boundary

M9 adds the `osca.ml` capability. It consumes governed dataset identity and later integrates with F2/F3 promotion boundaries, but it does not execute trades or automatically deploy retrained models.

## Contracts

The first slice defines immutable Pydantic contracts and deterministic service helpers for evaluation and promotion decisions.
