# U11 Requirement Traceability

| Requirement | Implementation | Automated evidence | Manual evidence |
|---|---|---|---|
| Safe versioned initialization | `operator_experience.initialize_profile`, `osca init` | `test_init_creates_safe_versioned_profile`, overwrite refusal test | Clean-profile init output and generated config |
| Structured corrective diagnostics | `operator_experience.doctor_profile`, `osca doctor` | pre-init failure and initialized-profile tests | Doctor JSON before and after workflow |
| Primary workspace startup | `osca workspace` wrapper | CLI discovery and non-loopback rejection tests | Workspace snapshot and local server health |
| Canonical local import | `osca import-data` alias | canonical command discovery; compatibility equivalence pending | Imported dataset revision |
| Canonical deterministic analysis | `osca analyze` alias | canonical command discovery; compatibility equivalence pending | Retained analysis report |
| Canonical backtest-to-paper | `osca backtest` alias | canonical command discovery; compatibility equivalence pending | Retained backtest/paper report |
| Canonical experiment/diagnostic/validation workflow | `osca research-pipeline` | existing U8/U10 pipeline tests | U11 retained pipeline manifest |
| Compatibility window | legacy commands retained; `quickstart.md` mapping | compatibility equivalence pending | Command comparison outputs |
| Cross-shell safety | `quickstart.md` zsh/Bash/PowerShell examples | documentation-link and command-help checks | Clean shell walkthrough |
| Safety boundaries | config, init/doctor outputs, loopback workspace guard | U11 focused tests plus inherited U9/U10 tests | Snapshot confirms read-only and disabled execution |

U11 does not authorize recommendations, automatic promotion, live model serving, broker connectivity, autonomous execution, real-capital orders, remote writes, or public evidence sharing.