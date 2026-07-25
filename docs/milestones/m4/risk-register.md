# M4 Risk Register

| Risk | Description | Treatment | Status |
|---|---|---|---|
| M4-R-001 | Project outputs lose the exact data and analysis dependencies needed for reproduction. | Require provenance on analysis graphs, outputs, visualizations, and timeline events. | Active |
| M4-R-002 | Analysis graph execution hides missing inputs or dependency cycles. | Validate graph shape before execution and fail closed on cycles, missing inputs, or duplicate nodes. | Active |
| M4-R-003 | Visualization specifications accidentally depend on private internal database shape. | Visualizations reference governed output identities and reproduction metadata only. | Active |
| M4-R-004 | Ad hoc exploration becomes untraceable once promoted. | Promotion records source workspace, selected dependencies, and captured rationale. | Active |
| M4-R-005 | M4 drifts into M5 external extension packaging or M6 backtesting. | Keep contracts internal and draft extension-compatible; defer independent packaging and strategy evaluation. | Active |
