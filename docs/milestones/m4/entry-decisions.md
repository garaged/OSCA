# M4 Entry Decisions

- **Status:** Accepted for initial M4 slice
- **Last reviewed:** 2026-07-24

## Decisions

| Decision | Outcome | Rationale |
|---|---|---|
| M4-D-001 | Use internal draft extension-compatible contracts for built-in analysis and visualization behavior. | M4 needs usable research-project behavior before M5 makes contracts independently packageable. |
| M4-D-002 | Reference governed analytical output identities from visualization specifications. | Prevents visualizations from depending on private database shape or bypassing provenance. |
| M4-D-003 | Keep ML training, backtesting, paper trading, and LLM orchestration out of M4. | Those behaviors have dedicated later milestones and higher risk gates. |

These decisions are bounded by ADR-0030 and do not supersede product decisions.
