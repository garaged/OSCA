# D4 Asset Catalog, Market Browser, and Watchlists

Status: In implementation

Baseline: D3 merge c170e5b2c93f70092ec955159759424d65c4ad64
Branch: agent/d4-asset-catalog-watchlists

## Outcome

D4 adds a searchable local asset catalog, a market browser, and profile-scoped persistent watchlists.

## Boundaries

- Python remains authoritative for asset identity, aliases, availability, watchlists, and persistence.
- Asset identity remains distinct from provider-specific symbols.
- Search works from local metadata and bundled seeds.
- Watchlists persist transactionally in SQLite.
- React continues to use the narrow desktop request bridge.
- Streaming prices, charting, recommendations, brokerage connections, and order execution are outside D4.

## Delivery slices

1. Specification, requirements, OpenSpec, traceability, and manual acceptance.
2. Asset identity and catalog application model.
3. Profile-scoped watchlist persistence and migration.
4. Desktop API methods and typed contracts.
5. Responsive market browser and watchlist UI.
6. Automated and manual validation.
7. Exit review and owner-directed merge.
