# P4 Risk Register

| ID | Risk | Treatment | Status |
|---|---|---|---|
| P4-R-001 | Adapter contracts imply live provider availability. | Keep network access disabled and document deferred runtime boundary. | Active |
| P4-R-002 | SEC fair-access constraints are under-modeled. | Require user-agent and fair-access policy in the contract. | Active |
| P4-R-003 | FRED API-key handling leaks credential values. | Require named API-key references only and no live credential materialization. | Active |
| P4-R-004 | Non-preferred providers become implementation-ready accidentally. | Contract validators reject non-SEC/FRED providers. | Active |
| P4-R-005 | Fixture evidence drifts from provider contract expectations. | Validate provider, endpoint, checksum shape, and non-empty records. | Active |
