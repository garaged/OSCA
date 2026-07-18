# Executable Architecture Backlog

- **Status:** Active
- **Governing role:** Quality authority
- **Architecture approval:** Architecture authority
- **Purpose:** Sequence repository controls without selecting deferred technology prematurely.
- **Review trigger:** Stack decision, M1 specification, or architecture finding
- **Last reviewed:** 2026-07-18

## Stack-independent bootstrap

| ID | Control | Trigger | Evidence | State |
|---|---|---|---|---|
| AUTO-001 | Markdown link and index validation | M0.x merge | Check output | Ready |
| AUTO-002 | YAML syntax validation | M0.x merge | Registry/manifest parse | Ready |
| AUTO-003 | Unique governed identifier validation | Registry expansion | Validation report | Specified |
| AUTO-004 | ADR index/status consistency | ADR change | Validation report | Specified |
| AUTO-005 | Stale exception and deadline detection | First exception | Scheduled report | Specified |
| AUTO-006 | Required artifact metadata lint | M1 intent/spec creation | PR check | Specified |
| AUTO-007 | Traceability dangling-reference detection | First M1 spec | PR check | Specified |

## Stack-dependent enforcement

| ID | Control | Decision trigger | Authority | State |
|---|---|---|---|---|
| AUTO-101 | Module graph and cycle enforcement | DD-001 and DD-002 | ADR-0003 | Deferred |
| AUTO-102 | Public/private import enforcement | DD-001 and DD-002 | ADR-0003 | Deferred |
| AUTO-103 | Cross-module persistence access detection | DD-003 | ADR-0009 | Deferred |
| AUTO-104 | Contract compatibility suites | First concrete contract format | ADR-0004 | Deferred |
| AUTO-105 | Secret, dependency, and supply-chain scanning | Build/runtime selection | Security architecture | Deferred |
| AUTO-106 | Coverage and risk-tier gate orchestration | Test/build selection | ADR-0005 | Deferred |
| AUTO-107 | Telemetry-contract conformance | First runnable slice | ADR-0010 | Deferred |
| AUTO-108 | Recovery and workflow-resume exercise | Persistence/workflow selection | ADR-0006, ADR-0007, ADR-0009 | Deferred |

## Backlog rule

“Deferred” means the governing obligation is accepted but its executable implementation awaits the named decision trigger. When a trigger becomes true, M1 planning must assign an owner, acceptance criteria, and delivery slice before dependent product code proceeds.
