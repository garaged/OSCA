# P1 Risk Register

| Risk | Description | Treatment | Status |
|---|---|---|---|
| P1-R-001 | Provider license terms are incomplete or ambiguous. | Missing permissions and warning findings block or defer promotion. | Mitigated by fail-closed gates |
| P1-R-002 | Secret values leak into provider evidence. | Credential records require named secret references and reject value-shaped references. | Mitigated by validation |
| P1-R-003 | Quota limits are too low for production-like use. | Promotion requires explicit quota policy and minimum headroom. | Mitigated by service tests |
| P1-R-004 | Production enablement is mistaken for live ingestion. | P1 docs and contracts limit scope to evidence and decisions only. | Mitigated by boundary docs |
| P1-R-005 | Provider-specific policy evidence drifts after approval. | Evidence retains review time, provider identity, and policy identifiers for re-review. | Accepted residual risk |
