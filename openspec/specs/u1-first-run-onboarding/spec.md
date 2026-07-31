# u1-first-run-onboarding Specification

## Purpose

Provide deterministic first-run diagnostics and workspace preparation for OSCA's local research path.

## Requirements

### Requirement: First-run readiness report

U1 SHALL report Python compatibility, platform support, writable storage, demo-fixture availability, and preserved execution boundaries as structured evidence.

#### Scenario: Supported clean machine is prepared
- **GIVEN** Python 3.13, a supported platform, and a repository checkout
- **WHEN** onboarding runs with `--prepare`
- **THEN** the storage root is created, all checks are ready, and the command exits successfully.

#### Scenario: Storage needs operator action
- **GIVEN** a missing storage root
- **WHEN** onboarding runs without `--prepare`
- **THEN** the report returns `action_required` and explains how to prepare the directory.

#### Scenario: Storage path is invalid
- **GIVEN** a storage path that is a file or cannot be written
- **WHEN** onboarding runs
- **THEN** the report returns `failed` without modifying unrelated paths.

### Requirement: Safety boundaries

U1 SHALL perform no network requests, credential resolution, provider calls, recommendations, broker execution, or real-capital behavior.

#### Scenario: Onboarding completes
- **WHEN** any onboarding report is produced
- **THEN** network, credentials, recommendations, broker execution, and real capital remain disabled.
