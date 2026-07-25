# m11-analytical-breadth-portfolio-intelligence Specification

## Purpose

Index the verified M11 analytical breadth and portfolio intelligence semantics under REQ-0134-REQ-0144 and ADR-0037.

## Requirements

### Requirement: Analysis pack manifests

M11 analytical packs SHALL declare family, version, supported asset classes, output kinds, data requirements, methodology, assumptions, limitations, and documentation.

#### Scenario: Documented manifest
- **GIVEN** an analysis pack manifest
- **WHEN** it is validated
- **THEN** methodology documentation and data-safety metadata are required.

### Requirement: Evidence synthesis

M11 analytical result and synthesis records SHALL preserve supporting and contradicting evidence references.

#### Scenario: Cross-family synthesis
- **GIVEN** multiple analytical result bundles
- **WHEN** synthesis is recorded
- **THEN** included results and evidence references are retained.

### Requirement: Comparison and calibration

M11 method comparison and outcome calibration records SHALL preserve compared results, preferred result when applicable, rationale, expected and realized outcomes, findings, and status.

#### Scenario: Invalid preferred method
- **GIVEN** a preferred result that was not compared
- **WHEN** method comparison is recorded
- **THEN** the comparison is blocked.

### Requirement: Portfolio and visualization intelligence

M11 portfolio scenario and visualization records SHALL preserve portfolio scenario evidence, accessibility summary requirements, and export metadata requirements.

#### Scenario: Visualization metadata
- **GIVEN** a visualization pack spec
- **WHEN** accessibility summaries or export metadata are disabled
- **THEN** validation fails closed.

### Requirement: Intelligence metadata persistence

M11 intelligence metadata SHALL persist pack, result, comparison, calibration, scenario, synthesis, and visualization records with scoped queries.

#### Scenario: Project query
- **GIVEN** result bundles for multiple projects
- **WHEN** one project is queried
- **THEN** only records scoped to that project are returned.
