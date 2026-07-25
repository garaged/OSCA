# M8 F3 Paper Evaluation Specification

- **Status:** Accepted
- **Milestone:** M8
- **Requirements:** REQ-0102-REQ-0112
- **ADR:** ADR-0034

## Purpose

M8 defines the governed F3 paper evaluation foundation that consumes approved F2 promotion evidence and produces forward paper-account evidence without live execution.

## Requirements

### REQ-0102: Independent paper accounts

Paper accounts must preserve stable identity, base currency, lifecycle status, creation time, and independence from research-project mutable state.

### REQ-0103: Approved candidate linkage

A paper evaluation candidate must reference an approved M7 promotion gate and must fail closed when the gate is not approved.

### REQ-0104: Paper run request identity

Paper evaluation requests must declare paper account, approved candidate, promotion gate, explicit data requirements, optional schedule identity, and timezone-aware request time.

### REQ-0105: Health gate authority

Paper processing must be blocked when data or operational health gates are blocked or when error findings exist.

### REQ-0106: Pause and kill-switch controls

Paper account pause and system kill-switch state must be explicit deterministic evidence before order processing.

### REQ-0107: No live execution implication

F3 paper state must not represent live brokerage/exchange execution or real-capital order placement.

### REQ-0108: Backtest-versus-forward comparison

Forward comparison records must preserve F2 request, F2 promotion gate, F3 paper run, metric methodology, findings, and comparison time.

### REQ-0109: Automation fail-closed boundary

Durable schedules, notification delivery, and recovery behavior must fail closed until their M8 slices define accepted contracts and tests.

### REQ-0110: Deferred scope visibility

M8 documentation must disclose deferred live execution, ML, LLM, provider promotion, and F4 fidelity scope.

### REQ-0111: Evidence-based completion

M8 is complete only when requirements, contracts, implementation, verification, documentation, traceability, risks, OpenSpec, and hosted Quality evidence are retained.

### REQ-0112: Manual testing and usage baseline

M8 establishes the first manual testing and usage document. Later milestone specifications must update that document when user-visible or operator-visible behavior changes, or record why no manual coverage change is required.
