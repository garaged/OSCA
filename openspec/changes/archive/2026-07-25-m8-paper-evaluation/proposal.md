# Proposal

## Why

M7 validates candidates historically through F2 event-driven evidence. OSCA now needs a governed forward paper-evaluation layer that can exercise approved candidates against forward data without crossing into live execution.

## What changes

- Add independent paper account and run identity.
- Link paper evaluation to approved M7 promotion gates.
- Add health gates, pause controls, and kill-switch state.
- Add backtest-versus-forward comparison evidence.
- Keep scheduling, notifications, persistence, and recovery in later M8 slices.

## Impact

- Adds M8 requirements REQ-0102-REQ-0111.
- Adds ADR-0034.
- Adds paper evaluation contracts and tests.
