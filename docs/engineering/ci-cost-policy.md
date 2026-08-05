# CI Cost and Validation Policy

OSCA preserves strong release and merge evidence while avoiding redundant hosted-runner consumption.

## Validation tiers

### Draft iteration

Draft pull requests run fast, Linux-first checks for affected components:

- Python lint, strict typing, tests, and architecture checks when Python or packaging inputs change;
- OpenSpec validation;
- secret scanning;
- desktop frontend, Rust broker, and desktop protocol checks when desktop paths change.

Cross-platform package lifecycle and contributor rehearsal do not run for every draft synchronization.

### Ready for review

Marking a pull request ready for review triggers the full merge-confidence suite, including supported Linux and macOS contributor and package-lifecycle validation. Later commits to a ready pull request continue to trigger full validation, but obsolete runs are cancelled automatically.

### Main and release validation

Pushes to `main` run the full supported-platform suite. Release-candidate acceptance and release artifact evidence run only for an explicit manual dispatch or a version tag, rather than for every pull-request commit.

## Concurrency

Each workflow uses one concurrency group per pull request or ref with `cancel-in-progress: true`. A newer commit supersedes validation of an older commit on the same pull request.

## Change-aware execution

Jobs may skip when their owned paths are unaffected during draft iteration. Skipping an unaffected component is not a waiver: ready-for-review, main, and release validation exercise the complete required suite.

## Commit batching

Repository automation and contributors should batch coherent changes before pushing. Preferred batches are:

1. intent and specification;
2. implementation;
3. tests and corrections;
4. final evidence and documentation.

Avoid one remote commit per generated or related file because each synchronization can schedule hosted work.

## Non-negotiable boundaries

Cost conservation must not:

- remove required validation before merge;
- eliminate macOS or Linux acceptance;
- weaken deterministic, architecture, OpenSpec, extension, migration, security, or secret-scanning gates;
- convert failed checks into ignored failures;
- substitute release evidence with unverified claims.
