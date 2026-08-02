# First-Run and Unified Operator Experience Delta Specification

## ADDED Requirements

### Requirement: Safe versioned initialization

The primary `osca` CLI SHALL initialize a local operator profile with versioned configuration and safe local defaults without requiring hand-authored JSON.

#### Scenario: New profile is initialized

- **WHEN** an operator runs `osca init` against an uninitialized profile root
- **THEN** OSCA creates versioned operator configuration and a writable storage root
- **AND** workspace access is loopback-only
- **AND** network access, recommendations, automatic promotion, broker connectivity, autonomous execution, and real-capital orders remain disabled.

### Requirement: Structured corrective diagnostics

The primary `osca` CLI SHALL provide deterministic readiness diagnostics with machine-readable checks and remediation.

#### Scenario: Profile is missing

- **WHEN** an operator runs `osca doctor` before initialization
- **THEN** the result is failed
- **AND** the missing configuration check contains an actionable `osca init` remediation
- **AND** no network, recommendation, broker, or execution capability is enabled.

### Requirement: Primary workspace startup

The primary `osca` CLI SHALL start or snapshot the analyst workspace without requiring `python -m osca.analyst_workspace`.

#### Scenario: Workspace is started

- **WHEN** an initialized operator runs `osca workspace`
- **THEN** the configured storage root, loopback host, and local port are used by default
- **AND** non-loopback hosts are rejected
- **AND** the workspace remains read-only.

### Requirement: Unified primary workflow

The primary `osca` CLI SHALL expose initialization, diagnostics, acquisition or local import, research execution, and workspace startup through documented canonical commands.

#### Scenario: Operator follows the quickstart

- **WHEN** a new user follows the canonical quickstart
- **THEN** no internal Python module invocation is required
- **AND** no JSON request document must be authored manually
- **AND** retained evidence is discoverable in the workspace.

### Requirement: Compatibility and shell safety

Existing operator entry points SHALL remain usable during a documented deprecation window, and canonical quickstarts SHALL be safe for zsh, Bash, and PowerShell.

#### Scenario: Existing command remains available

- **WHEN** an operator uses a documented compatibility entry point
- **THEN** behavior remains equivalent to the canonical command
- **AND** documentation identifies the canonical replacement and deprecation policy.

### Requirement: Safety boundaries remain disabled

All U11 primary commands SHALL preserve the U9/U10 provider, provenance, read-only, recommendation-disabled, promotion-disabled, broker-disabled, autonomous-disabled, and real-capital-disabled boundaries.

#### Scenario: Primary workflow is executed

- **WHEN** initialization, diagnostics, acquisition/import, research, or workspace commands run
- **THEN** network access remains explicit rather than implicit
- **AND** no recommendation, promotion, broker, autonomous, or real-capital capability is enabled.