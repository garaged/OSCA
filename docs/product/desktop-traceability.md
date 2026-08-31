# Desktop Product Traceability

Status: Active implementation baseline through D10

| Product intent | Governing milestones | Required evidence | Current disposition |
|---|---|---|---|
| Maintain one authoritative local-first core across CLI, desktop, workspace, and personal server | D1-D19 | Shared application-service tests and architecture checks | D1/D2 application API and frontend architecture tests active |
| Provide usable desktop onboarding and system diagnostics | D1-D3 | Clean-profile manual acceptance and failure-state tests | D2 implemented; cross-platform manual evidence pending |
| Preserve free/offline foundational functionality | D2-D19 | Offline acceptance path without paid provider credentials | D2 bundled deterministic synthetic import implemented |
| Provide governed asset discovery, analysis, and visualization | D4-D6 | Data lineage, numerical golden tests, chart accessibility evidence | D4 and D5 implemented; D6 specification baseline active |
| Provide reproducible strategy research | D7 | Versioned strategy definitions, fidelity disclosures, benchmark and sensitivity evidence | D7 accepted |
| Provide auditable virtual portfolios and simulated orders | D8-D9 | Double-entry invariants, deterministic replay, fill-assumption evidence, recovery tests | D8-D9 accepted |
| Provide leakage-resistant ML experimentation | D10-D11 | Point-in-time datasets, time-aware validation, baseline comparisons, approval and drift evidence | D10 active; D11 planned |
| Provide explainable, fail-closed recommendations | D12 | Structured recommendation records, contradictory evidence, policy and lineage tests | Gated and unavailable in D2 |
| Provide bounded AI assistance downstream of evidence | D13 | Grounding, tool authorization, injection resistance, budget, and provider tests | Gated and unavailable in D2 |
| Provide reliable automation without arbitrary-command scheduling | D14 | Typed workflow schemas, recovery, alert, and secure personal-server evidence | Planned |
| Provide governed reports and exports | D15 | Deterministic source records, provenance, redaction, and export-policy tests | Planned |
| Provide permissioned trusted-local extensions | D16 | Manifest, permission, impact-preview, execution-evidence, disable, and rollback tests | Planned/gated |
| Support Windows before polished release | D17 | Signed installer, updater, clean-VM, path, Unicode, credential, and notification acceptance | Planned |
| Meet accessibility, localization, reliability, and performance standards | D2-D18 | Automated and manual release-blocking evidence | D2 keyboard/focus/tokens/motion foundation implemented; D18 completion remains |
| Ship a signed, recoverable, broadly usable desktop release | D19 | Full platform matrix, migration, update, backup/restore, and no-live-order proof | Planned |

## D2 implementation trace

D2 is governed by:

- requirements `REQ-0282` through `REQ-0293` in `docs/governance/requirements-catalog-d2.md`;
- executable behavior in `docs/milestones/d2/specification.md`;
- requirement-to-code mapping in `docs/milestones/d2/traceability.md`;
- OpenSpec change `d2-desktop-shell-ux-foundation`;
- clean-profile procedure in `docs/milestones/d2/manual-acceptance.md`;
- draft pull request #81.

D2 preserves the D1 architecture:

- Python owns profile, diagnostics, storage, import, provider, recommendation, and execution meaning.
- React renders strict versioned responses and does not inspect files or databases.
- Rust remains a narrow supervised-sidecar IPC host with no domain logic or generic shell/filesystem authority.
- Recommendation, broker, exchange, autonomous, live-order, and real-capital behavior remains unavailable.

## Traceability rule

Each milestone executable specification must map its requirements to:

1. one or more rows in this product traceability baseline;
2. relevant accepted decisions and ADRs;
3. implementation and automated-test locations;
4. manual-acceptance evidence;
5. known limitations or explicit deferrals.

A milestone cannot pass exit review with unresolved requirements hidden only in prose or issue discussions.
