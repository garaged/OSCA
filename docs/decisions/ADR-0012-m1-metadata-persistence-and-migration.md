# ADR-0012 — M1 Metadata Persistence and Migration

- **Status:** Accepted
- **Date:** 2026-07-18
- **Decision owners:** Architecture authority and data owner
- **Scope:** Configuration snapshots, job state, catalog metadata, audit references, and recovery records introduced in M1
- **Related requirements:** REQ-0011 through REQ-0018
- **Related product decisions:** D-007, D-033, D-035, D-036, D-044
- **Supersedes:** DD-003 for M1 metadata state only
- **Superseded by:** None

## Context

M1 requires durable single-node state while preserving zero-service workstation operation. It does not yet introduce governed market-data payload storage.

## Decision

M1 metadata state will use SQLite in WAL mode through SQLAlchemy 2, with Alembic-owned migrations.

Each capability owns its schema objects and repositories. Cross-capability table access is prohibited. Transactions do not cross capability ownership except through an explicitly reviewed invariant.

Required database policies include:

- short transactions and explicit one-writer behavior;
- configured busy timeout and bounded retry classification;
- foreign-key enforcement;
- migration identity and forward-recovery behavior;
- integrity checks and isolated backup/restore tests;
- filesystem permission and secure-path validation;
- deterministic test databases;
- health reporting for lock, migration, integrity, and capacity state.

SQLite is not selected as the M2/M3 market-series analytical store. Large payloads and analytical storage remain separate decisions.

## Consequences

Local installation requires no database service and metadata backups remain portable. Write concurrency is bounded; M1 must expose contention instead of hiding it. SQLAlchemy preserves owned ports and testability, not an unsupported promise that all future databases are interchangeable.

## Fitness

- only owning capability repositories access their tables;
- migration from every retained schema fixture succeeds or produces defined forward-recovery behavior;
- interrupted migration and integrity failure are detected;
- concurrent job-state updates satisfy declared idempotency and lock behavior;
- backup/restore produces an equivalent verified metadata state.

## Revisit triggers

Measured write contention, personal-server availability evidence, unsupported migration requirements, or durability needs exceeding the governed SQLite envelope.
