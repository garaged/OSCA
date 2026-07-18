## Context

The accepted M1 specification requires installation, developer setup, configuration, security, interface, job, recovery, telemetry, troubleshooting, limitations, schemas, and executable examples. Focused job and recovery pages already exist. M1.7 must connect and validate them without creating duplicate normative sources.

## Goals and non-goals

### Goals

- Provide a single version-matched entry path from clean checkout to verified readiness.
- Route readers to focused job and recovery guidance.
- Automatically validate representative safe examples where practical.
- Retain exact validation and traceability evidence for REQ-0019 and REQ-0020.
- Correct stale M1 navigation and status references.

### Non-goals

- Rewriting accepted specifications or ADRs.
- Duplicating lifecycle, recovery, security, or compatibility rules.
- Claiming M1 exit approval before M1.8.
- Executing production recovery with example credentials or destinations.

## Decisions

### Documentation authority

The accepted specification and ADRs remain normative. The M1 guide is task-oriented, explicitly non-normative guidance. Focused diagnostic and recovery pages retain detailed procedures; the guide links rather than repeats them.

### Executable-example boundary

Automation validates deterministic, safe commands and semantic outcomes in an isolated temporary environment. Commands requiring a real credential-store identity, production recipient, or external custody ceremony are validated through existing adapter/CLI tests and clearly marked as operator-supplied examples.

### Evidence identity

The retained M1.7 record names the exact final source revision, locked dependency identity, tools, commands, results, limitations, and immutable CI run. Historical slice evidence remains unchanged.

## Risks and tradeoffs

- A broad guide can drift; keep it concise, link focused pages, and test commands and links.
- Platform-specific credential stores and dual-stack behavior cannot be proven by one CI environment; document the limitation and retain adapter evidence.
- Source identity is unknown until the final branch revision; the evidence record must not claim completion before CI validates that revision.

## Validation

- locked environment and clean migration;
- Ruff, strict mypy, and full pytest;
- architecture, schema, migration, and documentation link/example checks;
- representative CLI readiness and application startup checks;
- strict OpenSpec validation;
- secret scan;
- traceability inspection against REQ-0019 and REQ-0020.
