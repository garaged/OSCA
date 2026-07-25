# m4-research-projects-analytics Specification

## Purpose
Index the verified M4 research project, analytics, visualization, dashboard, and evidence-report semantics under REQ-0053-REQ-0068 and ADR-0030.

## Requirements

### Requirement: Governed research project identity

Research projects SHALL have stable identity, objective, horizon, lifecycle status, immutable creation metadata, and references to selected governed dataset revisions where applicable.

#### Scenario: Project creation
- **WHEN** a project is created with a non-empty objective and horizon
- **THEN** the record exposes a stable project identity, active lifecycle state, and immutable creation metadata

### Requirement: Project timeline and promotion

Project timelines SHALL record typed events for decisions, hypotheses, data revisions, analysis graphs, analytical outputs, visualizations, reports, and ad hoc promotions.

#### Scenario: Ad hoc workspace promotion
- **WHEN** an ad hoc workspace is promoted into a governed project
- **THEN** OSCA creates a project, promotion record, and timeline event with selected dependency identities preserved

### Requirement: Hypothesis lifecycle

Hypotheses SHALL capture assumptions, expected outcomes, invalidation conditions, confidence, and lifecycle state.

#### Scenario: Hypothesis evidence changes
- **WHEN** evidence weakens, confirms, invalidates, or expires a hypothesis
- **THEN** the state transition is explicit and records timeline evidence without erasing prior events

### Requirement: Analysis graph validation

Analysis graphs SHALL declare typed nodes, dependencies, input references, output references, parameters, interval requirements, and quality policy.

#### Scenario: Graph has invalid structure
- **WHEN** a graph has duplicate nodes, missing dependency targets, missing input references, dependency cycles, or unsupported provisional data use
- **THEN** validation fails before execution planning

### Requirement: Analytical output provenance

Analytical outputs SHALL distinguish output type and retain project, graph, dataset revision, parameter, producer, quality, effective-time, and evidence provenance.

#### Scenario: Output lacks dataset lineage
- **WHEN** an output is produced from governed market data without dataset revision references
- **THEN** validation fails before the output is retained

### Requirement: Evidence-backed reports

Evidence-backed reports SHALL reference structured outputs, visualizations, assumptions, contradictions, and reproduction metadata.

#### Scenario: Report references foreign visualization output
- **WHEN** a visualization references an analytical output outside the report
- **THEN** report assembly fails before the report is retained

### Requirement: Declarative visualization specifications

Visualization specifications SHALL reference governed analytical output identities and SHALL include export reproduction metadata.

#### Scenario: Visualization export
- **WHEN** a visualization is exported
- **THEN** the export metadata identifies source outputs, producer version, generation time, format, and aggregation or downsampling disclosure

### Requirement: Dashboard composition

Dashboard specifications SHALL compose panels from governed visualization specifications without mutating underlying analyses or outputs.

#### Scenario: Dashboard uses project visualizations
- **WHEN** a dashboard is composed from visualization specifications in the same project
- **THEN** the dashboard records stable panel metadata and source visualization identities

### Requirement: M4 scope boundary

M4 SHALL remain compatible with M3 temporal correctness and SHALL NOT implement independent extension packaging, ML training, backtesting, paper trading, or live execution.

#### Scenario: Extension package request
- **WHEN** a capability requires independent package import or activation
- **THEN** it is deferred to M5 rather than implemented in M4

### Requirement: Retained M4 evidence

The change SHALL retain requirements, contracts, implementation, verification, documentation, traceability, risks, OpenSpec, and hosted Quality evidence.

#### Scenario: M4 completion review
- **WHEN** M4 exit is proposed
- **THEN** strict OpenSpec validation and every applicable OSCA gate pass against the retained source revision with later milestone deferrals explicit
