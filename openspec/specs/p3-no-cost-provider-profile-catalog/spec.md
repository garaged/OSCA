# P3 No-Cost Provider Profile Catalog

## Purpose

Define the accepted P3 provider profile catalog behavior.

## Requirements

### Requirement: Provider Profile Contracts

OSCA SHALL represent no-cost provider catalog candidates through deterministic contracts carrying provider identity, cost model, payment requirement, access mode, capabilities, disposition, source URIs, constraints, and production-promotion boundary.

### Requirement: Default Candidate Profiles

OSCA SHALL provide default profiles for SEC EDGAR, FRED, Alpha Vantage, Nasdaq Data Link, Stooq, and Yahoo Finance unofficial paths with dispositions matching P2.

### Requirement: Implementation Readiness Classification

OSCA SHALL classify preferred candidates as ready for adapter-contract planning, conditional candidates as needing evidence, and research-only or excluded providers as blocked from default automated implementation.

### Requirement: No Provider Runtime Boundary

OSCA SHALL NOT implement provider adapters, invoke provider APIs, materialize credentials, alter runtime routing, or promote providers as part of P3.
