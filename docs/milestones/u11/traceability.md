# U11 Requirement Traceability

| Requirement | Implementation | Automated evidence | Manual evidence |
|---|---|---|---|
| Safe versioned initialization | `operator_experience.initialize_profile`, strict `OperatorConfig`, `osca init` | initialization, overwrite refusal, unsafe/unknown-field rejection tests | Clean-profile init output and generated config |
| Structured corrective diagnostics | `operator_experience.doctor_profile`, `osca doctor` | pre-init, initialized-profile, provider/credential, and evidence-warning tests | Doctor JSON before and after workflow |
| Runtime and storage readiness | Python, PyArrow, SQLite, writable-root, and loopback-port checks | focused doctor assertions | Pre/post workflow doctor outputs |
| Provider capability and credentials | explicit Kraken-public/no-cost and blocked-equity diagnostics | `test_doctor_reports_provider_credentials_and_evidence_state` | Doctor check interpretation |
| Retained-evidence consistency | `AnalystWorkspaceService.snapshot` inside doctor | empty-profile and malformed-evidence tests | Populated doctor and workspace snapshot |
| Primary workspace startup | `osca workspace` wrapper | CLI discovery and non-loopback rejection tests | Workspace snapshot and local server health |
| Canonical local import | `osca import-data` alias | canonical discovery and delegation test | Imported dataset revision |
| Canonical deterministic analysis | `osca analyze` alias | canonical discovery and delegation test | Retained analysis report |
| Canonical backtest-to-paper | `osca backtest` alias | canonical discovery and delegation test | Retained backtest/paper report |
| Canonical experiment/diagnostic/validation workflow | `osca research-pipeline` | inherited U8/U10 pipeline tests and command discovery | U11 retained pipeline manifest |
| Compatibility window | legacy commands retained; `quickstart.md` mapping | canonical-to-compatibility delegation test | Compatibility help outputs |
| Cross-shell safety | `quickstart.md` zsh/Bash/PowerShell examples | documentation-link and command-help checks | Clean shell walkthrough |
| Safety boundaries | literal-false config fields, init/doctor outputs, loopback workspace guard | U11 focused tests plus inherited U9/U10 tests | Snapshot confirms read-only and disabled execution |

U11 does not authorize recommendations, automatic promotion, live model serving, broker connectivity, autonomous execution, real-capital orders, remote writes, or public evidence sharing.
