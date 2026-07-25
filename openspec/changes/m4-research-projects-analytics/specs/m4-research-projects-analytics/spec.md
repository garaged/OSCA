# m4-research-projects-analytics Specification

## ADDED Requirements

### Requirement: Governed project identity

Research projects SHALL have stable identity, objective, horizon, status, and immutable creation metadata.

#### Scenario: Project creation
- **WHEN** a project is created with a non-empty objective and horizon
- **THEN** the record exposes a stable project identity and active lifecycle state

### Requirement: Hypothesis lifecycle

Hypotheses SHALL capture assumptions, expected outcomes, invalidation conditions, confidence, and lifecycle state.

#### Scenario: Hypothesis evidence changes
- **WHEN** evidence weakens, confirms, invalidates, or expires a hypothesis
- **THEN** the state transition is explicit and does not erase prior timeline events

### Requirement: Analysis graph validation

Analysis graphs SHALL declare typed nodes, dependencies, input references, output references, parameters, interval requirements, and quality policy.

#### Scenario: Graph contains a cycle
- **WHEN** node dependencies form a cycle
- **THEN** validation fails before execution planning

### Requirement: Analytical output provenance

Analytical outputs SHALL distinguish output type and retain project, graph, dataset revision, parameter, producer, quality, and evidence provenance.

#### Scenario: Output lacks dataset lineage
- **WHEN** an output is produced from governed market data without dataset revision references
- **THEN** validation fails before the output is retained

### Requirement: Declarative visualization specifications

Visualization specifications SHALL reference governed analytical output identities and SHALL include export reproduction metadata.

#### Scenario: Visualization export
- **WHEN** a visualization is exported
- **THEN** the export metadata identifies source outputs, producer version, generation time, format, and aggregation or downsampling disclosure

### Requirement: M4 scope boundary

M4 SHALL remain compatible with M3 temporal correctness and SHALL NOT implement independent extension packaging, ML training, backtesting, paper trading, or live execution.

#### Scenario: Extension package request
- **WHEN** a capability requires independent package import or activation
- **THEN** it is deferred to M5 rather than implemented in M4
