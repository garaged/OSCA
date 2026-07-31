# OSCA

OSCA is a modular market-intelligence and quantitative-research platform for stocks and cryptocurrencies.

The M0-M12 architecture and lifecycle roadmap is complete. P1-P5 established provider governance and operator visibility. P6-P8 now provide a usable no-cost local evidence path: import user-supplied OHLCV, generate deterministic research observations, and run a transparent backtest into a linked local paper-evaluation record. P8 is complete with successful macOS Apple Silicon/Python 3.13 manual evidence.

P9 is the current implementation candidate. It adds deterministic SEC fixture replay and explicit opt-in SEC EDGAR company-facts/submissions preview behind declared user-agent, fair-access, bounded-response, cache, and provenance controls. FRED live API access, key resolution, caching, and archival remain policy-blocked pending accepted licensing evidence. P10 and P11 remain the shortest path to coherent source routing and an approachable analyst workspace. Production ingestion, live providers beyond explicitly approved previews, recommendations, broker execution, autonomous trading, and real-capital orders remain disabled.

## Start here

1. [Architecture status](ARCHITECTURE_STATUS.md)
2. [Product requirements](docs/product-requirements.md)
3. [M0 architecture overview](docs/architecture/README.md)
4. [M0.x operationalization](docs/milestones/m0x/README.md)
5. [Architecture handbook](docs/handbook/README.md)
6. [Architecture decisions](docs/decisions/README.md)
7. [Engineering constitution](engineering/constitution.md)
8. [M1 milestone](docs/milestones/m1/README.md)
9. [Run and operate M1](docs/milestones/m1/operations-guide.md)
10. [M1 initiation checklist](engineering/bootstrap/m1-initiation-checklist.md)
11. [M2 milestone](docs/milestones/m2/README.md)
12. [M3 milestone](docs/milestones/m3/README.md)
13. [M4 milestone](docs/milestones/m4/README.md)
14. [M5 milestone](docs/milestones/m5/README.md)
15. [M6 milestone](docs/milestones/m6/README.md)
16. [M7 milestone](docs/milestones/m7/README.md)
17. [M8 milestone](docs/milestones/m8/README.md)
18. [Manual testing and usage](docs/testing/manual-testing.md)
19. [M9 milestone](docs/milestones/m9/README.md)
20. [M10 milestone](docs/milestones/m10/README.md)
21. [M11 milestone](docs/milestones/m11/README.md)
22. [M12 milestone](docs/milestones/m12/README.md)
23. [P1 milestone](docs/milestones/p1/README.md)
24. [P2 milestone](docs/milestones/p2/README.md)
25. [P3 milestone](docs/milestones/p3/README.md)
26. [P4 milestone](docs/milestones/p4/README.md)
27. [P5 milestone](docs/milestones/p5/README.md)
28. [P6 milestone](docs/milestones/p6/README.md)
29. [P7 milestone](docs/milestones/p7/README.md)
30. [P8 milestone](docs/milestones/p8/README.md)
31. [P9 milestone](docs/milestones/p9/README.md)
32. [P8-P9 requirements and traceability reconciliation](docs/governance/p8-p9-reconciliation.md)
33. [Remaining P milestone roadmap](docs/milestones/remaining-p-roadmap.md)

## Current local workflow

The supported P6-P8 walkthrough is documented in [P8 user testing quickstart](docs/milestones/p8/user-testing-quickstart.md). It imports `tests/fixtures/local_ohlcv/aapl_backtest_daily.csv`, confirms `row_count: 10`, captures the emitted `payload_uri`, and uses that exact payload for research and backtest-to-paper evidence.

The P9 preview workflow is documented in [P9 user testing quickstart](docs/milestones/p9/user-testing-quickstart.md). Start with deterministic SEC fixture replay. SEC network access is optional and explicit; FRED live use remains blocked.

## Governing baseline

- [Product requirements](docs/product-requirements.md)
- [Product decision log](docs/decision-log.md)
- [M0 overview](docs/milestones/m0/README.md)
- [M0 architecture review](docs/milestones/m0/architecture-review-record.md)
- [Architecture decisions](docs/decisions/README.md)
- [Document control](docs/governance/document-control.md)
- [Requirements catalog](docs/governance/requirements-catalog.md)
- [Traceability model](docs/governance/traceability-model.md)
- [P8-P9 reconciliation](docs/governance/p8-p9-reconciliation.md)

The product baseline was merged through PR #1 at commit `14f537b7ce359007a7767301b41a6b5aac776aec`. The M0 foundation was merged through PR #2 at commit `30746da69162777000fec6e686dcee29df6345b2`. Accepted decisions remain authoritative until explicitly superseded.

## Engineering system

- [Engineering constitution](engineering/constitution.md)
- [Decision matrix](engineering/decision-matrix.md)
- [AI contributor contract](engineering/ai-contributor-contract.md)
- [Architecture evolution policy](engineering/architecture-evolution-policy.md)
- [Architecture registry](engineering/architecture-registry.yaml)
- [Engineering bootstrap](engineering/bootstrap/README.md)
- [OpenSpec integration policy](docs/governance/openspec-integration.md)
- [Architecture validation](docs/validation/README.md)
- [Manual testing and usage](docs/testing/manual-testing.md)
