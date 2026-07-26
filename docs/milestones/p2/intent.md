# P2 Intent - No-Cost Provider Discovery and Selection

## Intent

P2 establishes a governed discovery and selection baseline for no-cost provider candidates so OSCA can preserve useful functionality without requiring user spend.

The milestone records provider candidates, official-source evidence, cost model, capability fit, licensing and quota uncertainty, operational constraints, and recommended disposition before any implementation milestone adds adapters or retrieval behavior.

## Problem

P1 guarantees that no-cost providers can be promoted when evidence is complete, but OSCA still needs a curated list of additional no-cost sources and explicit exclusion rules. Without that, future work may either over-focus on paid providers or accidentally integrate popular but legally ambiguous sources.

## Outcome

P2 produces:

- A no-cost provider discovery catalog.
- A selection policy that prefers official APIs, clear terms, and bounded use.
- Explicit candidate and exclusion statuses.
- Requirements, specification, ADR, traceability, and manual review coverage for the discovery baseline.

## Scope Guard

P2 is documentation and governance only. It does not implement adapters, call external APIs, materialize credentials, enable retrieval, or change production promotion decisions.
