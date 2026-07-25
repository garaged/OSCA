# M3 Risk Register

| Risk | Description | Treatment | Status |
|---|---|---|---|
| M3-R-001 | Incorrect stock session assumptions mark bars missing when the market was closed. | Require accepted session evidence; unresolved is not repair eligible. | Active |
| M3-R-002 | Intraday incomplete bars are accidentally published as complete. | Completed-bar cutoff requires interval close plus publication lag. | Active |
| M3-R-003 | Resampling hides partial lower-interval coverage. | Emit no derived bar unless source coverage is contiguous and complete. | Active |
| M3-R-004 | M3 breaks accepted M2 daily contracts. | Add temporal contracts beside M2 daily contracts; retain compatibility tests. | Active |
| M3-R-005 | Provider licensing ambiguity expands through intraday scope. | Keep provider production promotion deferred until exact evidence is accepted. | Active |
