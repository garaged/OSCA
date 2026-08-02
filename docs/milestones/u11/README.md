# U11 — First-Run and Unified Operator Experience

- **Status:** Implementation complete; clean-profile acceptance pending
- **Baseline:** U10 merged through PR #73 at `4711c6f2f4ba17a0904515c6ca935e653cbee6ed`
- **Branch:** `agent/u11-first-run-operator-experience`
- **Implementation PR:** #74

## Intent

Let a technically capable new user complete OSCA's primary local research workflow through the primary `osca` CLI without invoking internal Python modules or hand-authoring JSON.

## Delivered outcome

1. `osca init` creates strictly validated versioned local configuration and a writable data root with safe defaults.
2. `osca doctor` reports machine-readable Python, PyArrow, SQLite, storage, port, provider, credential, and evidence-consistency checks with remediation.
3. `osca workspace` starts or snapshots the read-only workspace from operator configuration and rejects non-loopback hosts.
4. `osca import-data`, `osca analyze`, and `osca backtest` provide canonical operator names while retaining compatibility entry points through U13.
5. `osca research-pipeline` remains the canonical combined experiment, diagnostic, and human-gated local-validation path.
6. zsh, Bash, and PowerShell quickstarts describe one coherent installation-to-workspace workflow.
7. The root README and central manual-testing guide use the canonical U11 path.
8. OpenSpec, traceability, focused tests, manual acceptance, and exit-review authority are present.

The strict configuration contract rejects unknown fields and refuses attempts to enable network-by-default, recommendations, automatic promotion, brokers, autonomous execution, or real-capital orders.

## Validation

Quality run #713 passed on the foundation head. The final implementation-closeout head must pass the same complete hosted suite before manual acceptance:

- Ruff;
- strict mypy;
- tests, contracts, migrations, links, and architecture checks;
- OpenSpec doctor and strict validation;
- secret scanning.

## Remaining gate

Run [U11 clean-profile manual acceptance](manual-acceptance.md) and record the retained outputs in the [U11 exit review](exit-review.md).

The exit evidence must prove that a new profile can be initialized, diagnosed, populated through acquisition or import, processed through the retained research pipeline, and inspected through `osca workspace` without hand-authored JSON or internal module commands.

## Next milestone

U12 owns isolated installation, supported macOS/Linux packaging, upgrades, backup-before-migration, failed-upgrade recovery, and rollback evidence.

## Safety

U11 does not enable recommendations, automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, or public evidence sharing.
