# M6 Risk Register

| Risk | Description | Treatment |
|---|---|---|
| M6-R-001 | Look-ahead or revised data contaminates strategy validation. | Require explicit data-availability metadata and fail closed on revised-after-fact inputs. |
| M6-R-002 | Vectorized estimates are mistaken for authoritative event simulations. | Require fidelity profile and execution mode compatibility. |
| M6-R-003 | Provisional data enters event-driven or forward-paper behavior. | Reject provisional data for event-driven and forward-paper profiles. |
| M6-R-004 | Order intents are confused with live orders. | Keep order intents scoped to backtesting contracts and retain no live execution adapter. |
| M6-R-005 | Paper trading is started before journal/accounting authority exists. | Block F3 forward-paper plans until paper-account authority is introduced. |
