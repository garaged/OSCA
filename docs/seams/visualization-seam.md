# Visualization Seam

- **Status:** Draft
- **Owner:** Visualization and reporting capability
- **Purpose:** Render typed analytical results through declarative, portable, accessible specifications rather than arbitrary internal queries or executable frontend code.

## Contract groups

- visualization specification and schema;
- data and result references;
- interaction and parameter model;
- rendering request and output manifest;
- export and reproduction metadata;
- accessibility description and fallback table.

## Mandatory behavior

- Specifications reference governed results or typed datasets.
- Units, currency, timezone, effective time, quality, freshness, approximation, and provenance remain inspectable.
- Aggregation and downsampling are declared and reproducible.
- Rendering is deterministic for a fixed specification, data reference, renderer version, fonts or assets, and output profile where practical.
- Static rendering does not require the interactive web client.
- Custom views use a separately permissioned extension interface and cannot access unrelated application state.
- LLM chart requests compile to validated specifications, never arbitrary executable code.
- Keyboard use, screen-reader descriptions, non-color encodings, and accessible summaries are contract concerns.

## Conformance evidence

Golden or semantic fixtures cover schema validation, unsupported marks, approximation disclosure, missing data, accessibility metadata, static export, underlying-data export, and reproduction manifests.