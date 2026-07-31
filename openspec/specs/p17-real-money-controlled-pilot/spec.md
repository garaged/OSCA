# p17-real-money-controlled-pilot Specification

## Purpose

Preserve the P16 NO-GO decision and prevent unauthorized real-money execution work.

## Requirements

### Requirement: P17 remains blocked

P17 SHALL remain blocked while ADR-0044 is authoritative.

#### Scenario: P17 implementation is requested
- **GIVEN** ADR-0044 records a NO-GO decision
- **WHEN** broker, credential, order, reconciliation, sandbox, production, or pilot work is proposed
- **THEN** the proposal is rejected as not authorized.

### Requirement: Existing surfaces cannot place orders

Research, paper evaluation, model previews, schedulers, and extension packs SHALL remain unable to submit real orders.

#### Scenario: An existing surface attempts execution
- **GIVEN** an existing OSCA workflow
- **WHEN** it attempts to initiate a real-capital order
- **THEN** OSCA fails closed or reports a policy-blocked state.

### Requirement: Reconsideration requires supersession

P17 SHALL be reconsidered only after every P16 control-matrix blocker is closed and an accepted ADR explicitly supersedes ADR-0044.

#### Scenario: Reconsideration is proposed
- **GIVEN** a future execution proposal
- **WHEN** any control blocker remains open or no superseding ADR exists
- **THEN** P17 remains blocked.
