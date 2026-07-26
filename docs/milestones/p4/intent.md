# P4 Intent - No-Cost Provider Adapter Contracts

P4 defines deterministic, fixture-backed adapter contracts for the preferred no-cost provider profiles selected in P3: SEC EDGAR and FRED.

P4 exists to make the next implementation step precise before any live network access is added. It records provider-specific endpoints, credential requirements, fair-access or quota constraints, request identity, fixture validation, and fail-closed boundaries.

P4 must not implement live provider calls, materialize credential values, change runtime routing, promote providers, or enable production ingestion.
