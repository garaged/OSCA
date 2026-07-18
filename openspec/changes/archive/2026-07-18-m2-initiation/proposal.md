## Why

The accepted M1 baseline is complete and the PRD identifies M2 as the next milestone, but no M2 intent, stable requirements, contracts, risks, decisions, or evidence plan existed. This change creates the governed initiation package without beginning provider or data implementation.

## What Changes

- Propose the thin governed daily-data intent and M2/M3 boundary.
- Propose REQ-0021–REQ-0040 and M2-AC-001–M2-AC-020.
- Allocate Instrument, Provider, Market Data, Catalog, Workflow, Operations, Recovery, and interface ownership.
- Propose provider/instrument/daily-data/retrieval/quality/cleanup contract semantics.
- Define entry decisions, provider and persistence criteria, risk treatments, execution sequence, and evidence gates.
- Update navigation, traceability, architecture activity, and registry to M2 initiation.

## Capabilities

### New Capabilities

- `m2-governed-daily-data`: Initiation view for canonical instruments, provider adapters, and governed daily retrieval.

### Modified Capabilities

None. M1 contracts and implementation remain unchanged.

## Impact

- **Proposed requirements:** REQ-0021–REQ-0040.
- **Product authority:** PRD M2 and sections 8, 10–14, 37–39; D-012–D-018, D-040.
- **Architecture:** Frozen ADR-0001–ADR-0010 and accepted ADR-0011–ADR-0016 remain governing; new M2 decisions are gated.
- **Risk class:** Governed high-risk planning for data integrity, licensing, external adapters, persistence, cleanup, and migrations.
- **Non-goals:** Provider selection, storage selection, implementation, live-network CI, M3 intraday behavior, or milestone approval through OpenSpec.
