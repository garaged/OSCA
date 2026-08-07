# D4 Specification — Asset Catalog, Market Browser, and Watchlists

## 1. Canonical asset identity

Each asset has a stable profile-local identifier independent from provider symbols. The canonical record includes asset class, canonical symbol, display name, venue when applicable, quote currency when applicable, aliases, provenance, lifecycle status, and timestamps.

Provider aliases map to canonical assets and never become the primary identity. Ambiguous aliases return an explicit ambiguity result instead of silently selecting an asset.

## 2. Catalog sources

The catalog is composed from:

- bundled deterministic seed assets;
- assets observed in governed local imports;
- assets observed in admitted historical acquisitions;
- explicit user registration;
- optional admitted-provider enrichment in later slices.

Catalog browsing and watchlists must remain usable offline.

## 3. Search and filtering

Search is deterministic and case-insensitive across canonical symbol, display name, aliases, venue, and quote currency. Filters include asset class, lifecycle state, venue, and local-data availability.

Results are ordered by exact canonical-symbol match, exact alias match, prefix match, then normalized display-name match. Stable identifiers break ties.

## 4. Availability summary

Asset detail exposes local evidence only: known datasets, available timeframes, earliest and latest retained observation, provider/source provenance, and freshness classification derived from stored metadata. The UI must not imply streaming or real-time availability.

## 5. Watchlists

Watchlists are profile-scoped entities with stable identifiers, unique normalized names, optional descriptions, explicit ordering, and ordered canonical asset memberships.

Supported operations:

- create;
- list;
- rename and edit description;
- delete;
- add or remove an asset;
- reorder assets;
- reorder watchlists.

All mutations are transactional and idempotent where practical. Deleting a watchlist does not delete assets or market data.

## 6. Persistence and recovery

SQLite is authoritative for asset metadata, aliases, watchlists, and ordering. Schema changes use Alembic. Reads tolerate an empty profile. Writes fail closed on incompatible profile versions, lock contention, invalid identifiers, duplicate names, or ambiguous asset references.

## 7. Desktop application API

Python exposes typed request/response methods for:

- `asset.catalog.search`;
- `asset.catalog.detail`;
- `asset.catalog.register`;
- `watchlist.list`;
- `watchlist.create`;
- `watchlist.update`;
- `watchlist.delete`;
- `watchlist.membership.set`;
- `watchlist.reorder`.

React accesses these methods only through the existing `desktop_request` bridge. Rust gains no generic database, filesystem, network, or secret authority.

## 8. Desktop UX

D4 adds a first-class Markets area with:

- search and filter controls;
- result list with canonical identity and local availability;
- asset detail panel;
- watchlist sidebar and membership controls;
- empty, loading, error, ambiguity, and locked-profile states;
- keyboard navigation, visible focus, reduced-motion, forced-colors, and narrow-layout support.

## 9. Performance budgets

On a catalog of 50,000 assets and 100 watchlists:

- normalized local search p95 is at most 150 ms after database open;
- first result page returns at most 100 items;
- watchlist mutation p95 is at most 250 ms excluding lock wait;
- UI remains responsive through pagination or virtualization.

## 10. Safety and non-goals

D4 does not add streaming quotes, charting, quantitative analysis, recommendation ranking, alerts, portfolio ownership, brokerage connections, or order execution. Provider enrichment must reuse D3 policy and explicit network-consent boundaries.

## 11. Exit criteria

- Requirements and OpenSpec validation pass.
- Unit, integration, migration, desktop API, frontend, architecture, and persistence tests pass.
- Clean-profile manual acceptance passes on macOS ARM64 and Linux x86-64.
- Large-catalog performance evidence is retained.
- Accessibility, recovery, ambiguity, and profile-lock behavior pass.
- Traceability and exit review are reconciled before owner-directed merge.
