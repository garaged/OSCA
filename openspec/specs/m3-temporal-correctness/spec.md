# m3-temporal-correctness Specification

## Purpose
Index the verified M3 temporal correctness semantics for approved intervals, UTC bar windows, stock exchange sessions, crypto UTC boundaries, completed bars, calendar-aware gaps, resampling lineage, interval-aware dataset identity, governed OHLCV payloads, and non-daily publication under REQ-0041-REQ-0052 and ADR-0029.

## Requirements

### Requirement: Approved interval contract

Market Data SHALL support exactly `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, and `1d` interval identifiers for M3 interval-aware contracts.

#### Scenario: Unknown interval
- **WHEN** a caller supplies an interval outside the approved set
- **THEN** validation fails closed before retrieval, repair, publication, or resampling

### Requirement: Completed-bar semantics

Every interval bar SHALL use UTC start-inclusive/end-exclusive windows and SHALL be complete only when its interval end plus declared publication lag has passed.

#### Scenario: Current interval is still open
- **WHEN** a requested window ends after the completed-bar cutoff
- **THEN** it is classified incomplete and is not repair eligible

### Requirement: Stock session-aware gaps

Stock expected windows SHALL be derived from accepted exchange-session evidence.

#### Scenario: Calendar evidence is unavailable
- **WHEN** a stock session is not accepted for a requested interval
- **THEN** the interval is unresolved rather than missing and repair is not automatic

### Requirement: Crypto UTC boundaries

Crypto expected windows SHALL be derived from UTC day boundaries.

#### Scenario: Completed crypto interval missing
- **WHEN** a crypto interval has closed under the UTC boundary model and no observation exists
- **THEN** it is missing and repair eligible

### Requirement: Resampling lineage

Resampling SHALL derive higher intervals only from contiguous complete lower-interval bars and SHALL record every source bar identity.

#### Scenario: Lower interval coverage is partial
- **WHEN** the source bars do not fully cover the target window
- **THEN** no higher-interval bar is published

### Requirement: Interval-aware dataset identity

Dataset manifests, retrieval requests, storage inspection, canonical revision selection, and retention protection SHALL carry interval identity so accepted daily and intraday revisions cannot silently substitute for each other.

#### Scenario: Intraday revision exists beside daily revision
- **WHEN** a caller requests an exact interval
- **THEN** resolution considers only ready canonical revisions for that interval and preserves protected canonical history

### Requirement: Governed OHLCV payloads

Non-daily and resampled OHLCV bars SHALL use a governed Parquet schema with interval, UTC window, completion, exact OHLCV decimals, source identity, request identity, normalization revision, and calendar revision.

#### Scenario: Payload round trip
- **WHEN** OHLCV bars are serialized and deserialized
- **THEN** the exact governed schema metadata and row semantics are preserved

### Requirement: OHLCV publication workflow

Non-daily OHLCV publication SHALL use an interval-aware intent, deterministic payload encoding, staged manifest publication, interval-scoped object keys, idempotent fingerprint reuse, and protected canonical history.

#### Scenario: Publication interval mismatch
- **WHEN** OHLCV bars do not match the declared publication interval
- **THEN** publication fails before creating a ready canonical manifest

### Requirement: Retained M3 evidence

The change SHALL retain contract, temporal, retrieval, repair, resampling, persistence, payload, publication, retention, documentation, architecture, traceability, and hosted Quality evidence.

#### Scenario: M3 completion review
- **WHEN** M3 exit is proposed
- **THEN** strict OpenSpec validation and every applicable OSCA gate pass against the retained source revision with provider promotion deferrals explicit
