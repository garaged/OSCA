# D10 ML Lab Manual Acceptance Runbook

The exact-head automated suite is authoritative for dataset integrity, feature/label contracts, leakage controls, split arithmetic, baseline metrics, persistence, cancellation, recovery, ownership, and source boundaries. Human acceptance reviews only usability and meaning that automation cannot judge.

## Automated baseline

```bash
make acceptance-check
make acceptance-seed
make acceptance-run
```

The seeded profile already contains paired 220-row synthetic datasets, one completed ridge experiment, and a typed project pin.

## Required human path (target: 5-10 minutes)

1. Open **ML Lab** and confirm its purpose and no-promotion/no-recommendation/no-execution boundaries are immediately understandable.
2. Inspect the three feature definitions. Confirm the transformation, lookback, point-in-time safety, and missing-data meaning are readable.
3. Retain one regression or classification experiment plan. Confirm dataset revision, policies, split, purge/embargo, and resource bounds are visible before execution.
4. Run it and inspect the chronological partitions plus model-versus-baseline table. Confirm test evidence cannot be mistaken for model approval or a trading recommendation.
5. Restart OSCA, reopen the profile, and confirm the retained experiment, digest, and status remain visible. This restart probe is required only for the first supported platform unless persistence/recovery changed afterward.
6. Keyboard through the form, registry, and evidence table. Check increased text/zoom, narrow width, visible focus, forced/high contrast where available, and that status meaning is not color-only.
7. In Projects, confirm `ML experiment` is available as a typed pin and the seeded ML pin does not embed provider data.

Record PASS/FAIL for macOS ARM64 and Linux x86-64, exact head, automated gate results, findings, and any exploratory probes exercised or waived.

## Triggered exploratory probes

Run cancellation, insufficient-data, changed-dataset, interrupted-run, newer-schema, or second-process ownership probes manually only when their implementation or UI changed and automated evidence does not settle the human-visible question.
