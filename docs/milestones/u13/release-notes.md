# OSCA First Release-Candidate Notes

- **Candidate version:** Pending explicit U13 version decision
- **Candidate tag:** Pending successful final acceptance and explicit tag action
- **Supported platforms:** macOS Apple Silicon and Linux x86-64

## Delivered capabilities

- governed no-cost Kraken historical acquisition with explicit network opt-in;
- governed CSV and Parquet offline import fallback;
- deterministic analysis, backtesting, and paper-evidence generation;
- governed local ML experiments, diagnostics, and human-gated validation;
- read-only evidence workspace with lineage, filtering, raw JSON, and governed export;
- unified `osca` initialization, diagnostics, research, and workspace commands;
- isolated wheel installation through `uv tool`;
- version, checksum, SBOM, and provenance reporting;
- compatibility inspection, verified backup, safe restore, upgrade, failed-upgrade recovery, and rollback;
- official sixteen-area release-candidate acceptance and defect gate.

## Safety boundaries

OSCA does not provide authoritative investment recommendations. Automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, and public evidence publication remain disabled. ADR-0044 remains NO-GO and P17 remains blocked.

## Provider boundary

Kraken public spot OHLC is admitted for explicit internal-use acquisition. No no-cost equity provider currently passes the complete admission gate; governed CSV or Parquet import remains the supported equity fallback.

## Release publication

Tag creation, artifact signing, package-index publication, and public release publication require explicit actions and are not performed by the acceptance runner.
