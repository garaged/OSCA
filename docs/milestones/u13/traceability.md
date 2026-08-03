# U13 Release-Candidate Acceptance Traceability

| Acceptance area | Primary retained authority |
|---|---|
| Installation and initialization | U11 quickstart, U12 package lifecycle, hosted package matrix |
| No-cost historical acquisition | U9 exit review and governed Kraken evidence |
| Local CSV fallback | U11 quickstart and central manual testing |
| Dataset quality, revision, and lineage | U9 and U10 exit reviews |
| Deterministic analysis | Central manual testing and hosted test suite |
| Backtesting and paper evidence | Central manual testing and P8 retained evidence |
| ML experiment and diagnostics | U8 exit review and hosted test suite |
| Human-gated validation | U8 exit review |
| Workspace browsing and export | U10 exit review |
| Backup and restore | U12 exit review and hosted package matrix |
| Extension boundaries | Root README and central manual testing |
| Offline operation | U11 quickstart |
| Provider outage, quota, and policy | U9 exit review |
| Corrupt and incomplete artifacts | U10 and U12 exit reviews |
| Upgrade and rollback | U12 exit review and hosted package matrix |
| Documentation and CLI agreement | README, manual testing, primary CLI, document-link checks |

## Machine-readable enforcement

`scripts/generate_rc_acceptance_input.py` verifies that every normative area has retained evidence authority and that candidate artifacts exist. `osca-rc-acceptance evaluate` validates the exact matrix, defect dispositions, artifact references, and safety fields before producing a digest-addressed eligibility result.

## Defect authority

`docs/milestones/u13/defects.json` is the machine-readable defect registry. Open critical or high defects deny eligibility. Open medium defects require workaround, owner, and target milestone.

## Tag authority

The evaluator may recommend a version-derived tag only after all gates pass. It never creates a tag or publishes artifacts.
