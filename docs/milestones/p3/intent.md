# P3 Intent - No-Cost Provider Profile Catalog

## Intent

P3 converts the P2 no-cost provider discovery baseline into executable provider profile contracts so implementation planning can select safe candidates deterministically.

## Problem

P2 records provider dispositions in documentation. Future adapter work should not re-interpret those dispositions by hand or accidentally treat excluded or research-only sources as implementation-ready.

## Outcome

P3 adds a provider catalog module with deterministic profile contracts, default no-cost provider profiles, implementation-readiness classification, and tests that preserve the P2 candidate decisions in code.

## Non-goal

P3 does not create adapters, call external provider APIs, store credentials, change routing, or promote providers to production.
