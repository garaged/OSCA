# D9 Manual Acceptance — Forward Paper Evaluation and Simulated Orders

## Preconditions

- Use disposable profile state.
- Use local/synthetic governed bar data only.
- Use a D8 virtual portfolio with known starting cash.
- Do not configure broker/exchange credentials; D9 must not require or expose them.
- Complete automated validation and hosted CI before final acceptance.
- Execute the required human-judgment path in the detailed [D9 Paper Lab acceptance runbook](../../testing/d9-paper-lab-manual-acceptance.md) on each supported platform. Run its exploratory sections only when their stated triggers apply.

## Acceptance flow

1. Use the runbook's required path to create/select the retained account and D8 portfolio, retain a run, create/confirm one simulated draft, process one eligible local bar, and inspect the linked accounting effect.
2. Confirm the Paper Lab safety language, account/control, evidence/provenance, lifecycle/rejection feedback, and forward-vs-backtest wording are understandable without relying only on color.
3. Perform keyboard, normal and increased-text/zoom, and narrow-width review of the changed Paper Lab surface.
4. Perform the final source/product boundary check: no broker/exchange destination, credentials, live-order API, real-capital action, autonomous live execution, recommendation-to-order shortcut, arbitrary code, or paid-provider dependency.

The detailed runbook maps the remaining semantic cases to automated tests and declares the recovery, concurrency, package/platform, and non-default interaction scenarios that trigger exploratory acceptance.

## Platform coverage

Final D9 acceptance should cover macOS ARM64 and Linux x86-64, matching D8 supported desktop coverage.

## Evidence recording

Record exact commit, platform/package, hosted checks, PASS/FAIL per runbook section, any accepted limitations, and manual findings in `validation-evidence.md`. Do not mark `exit-review.md` complete before the evidence exists.
