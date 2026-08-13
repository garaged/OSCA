# D6 Research Projects, Saved Workspaces, and Integrated Evidence

## Why

D5 provides governed charting, quantitative analysis, saved Workbench views, and full-resolution exports. Users still need a desktop way to organize those assets, datasets, views, notes, decisions, and evidence into reproducible project context instead of leaving them as disconnected artifacts.

## What changes

- Add profile-scoped research project lifecycle and metadata.
- Add typed immutable pins to governed assets, watchlists, dataset revisions, Workbench views, exports, and reports.
- Add append-only project timeline events for lifecycle, pins, notes, workspace saves, exports, clone/archive/restore, and recovery-relevant changes.
- Add user notes that remain clearly separate from generated or calculated evidence.
- Add saved project workspaces that restore declarative desktop context without mutating evidence.
- Add governed thin manifest export with schema/version, provenance, broken-link disclosure, and no self-contained provider-data packaging.
- Add accessible responsive Projects UI and narrow typed desktop APIs under the existing ownership boundary.

## Boundaries

Python remains authoritative for project persistence, validation, migration, timeline, notes, pins, workspaces, and export. React renders typed state and captures declarative intent only. Rust remains the existing transport/session broker. D6 adds no executable notebook authority, recommendation generation, strategy execution, model training, provider credential collection, brokerage connectivity, paper orders, or real-capital execution.

## Requirements

This change implements REQ-0341 through REQ-0356 in `docs/governance/requirements-catalog-d6.md`.
