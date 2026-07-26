# P5 Risk Register

| ID | Risk | Treatment | Status |
|---|---|---|---|
| P5-R-001 | M0-M12 or P1-P4 docs overclaim runtime behavior. | Review authority chain and correct status to implemented, specified-only, fixture-backed, or deferred. | Active |
| P5-R-002 | Provider governance exists in code but is not reachable by operators. | Add narrow CLI/API inspection surfaces before new provider runtime work. | Active |
| P5-R-003 | Drift fixes accidentally change product scope. | Keep P5 changes corrective unless a new decision is explicitly required. | Active |
| P5-R-004 | Operator surfaces imply live provider availability. | Preserve fail-closed deferred-boundary messages. | Active |
| P5-R-005 | P6 starts before the baseline is clean. | Make P5 the required next implementation milestone. | Active |
