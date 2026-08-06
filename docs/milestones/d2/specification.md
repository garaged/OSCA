# D2 Specification — Desktop Shell and User Experience Foundation

- **Status:** In progress
- **Governing role:** Product and architecture authority
- **Approval roles:** Product, architecture, security, accessibility, and quality authorities
- **Purpose:** Define implementation-ready behavior and constraints for the first usable OSCA desktop shell, onboarding, profile, diagnostics, sample-data, state, and accessibility foundations.
- **Governing intent:** `docs/milestones/d2/intent.md`
- **Related decisions:** ADR-0001, ADR-0002, ADR-0003, ADR-0004, ADR-0005, ADR-0015, ADR-0039, ADR-0040, ADR-0044, ADR-0046
- **Related product authority:** `docs/product/desktop-product-intent.md`, `docs/product/cross-cutting-requirements.md`, `docs/product/desktop-capability-map.md`, `docs/product/desktop-traceability.md`
- **Downstream consumers:** Python desktop application API, Rust desktop broker, React frontend, automated tests, hosted validation, manual testing, and D3-D19 milestones

## Problem and context

D1 proved the desktop architecture and a minimal health vertical slice, but the current frontend remains a developer preview. Navigation is disabled, profile behavior is inspection-only, failure handling is minimal, and the application does not yet guide a new user through an honest offline first run.

D2 turns the accepted architecture into a reusable user-experience foundation without widening OSCA's financial, provider, credential, filesystem, or execution authority. Python remains the authoritative application and domain layer. React presents typed application responses. Rust remains a narrow lifecycle and IPC broker.

The D1 hosted-validation exception is a D2 prerequisite. D2 may begin specification and implementation work, but it cannot exit until the deferred supported-platform hosted validation has been rerun and any product defect has been corrected.

## Scope

### In scope

- Responsive desktop application shell and primary navigation.
- Versioned design tokens and reusable accessible UI primitives.
- First-run onboarding that explains the product and reaches a usable offline home surface.
- Profile list, inspect, create, select, and open application-service flows.
- Loading, empty, unavailable, retryable, blocked, and application-level error states.
- System diagnostics surface using authoritative application responses.
- Deterministic bundled sample-data import using retained synthetic fixture provenance.
- Keyboard navigation, visible focus, logical focus transfer, reduced motion, contrast, semantic structure, and screen-reader foundations.
- Persistent display of research-only, local-storage, optional-network, provider, credential, recommendation, and live-execution boundaries.
- D1 deferred hosted-validation evidence and D2 validation evidence.

### Out of scope

- Provider credential entry or credential-store integration.
- Provider acquisition or implicit network access.
- Production charts, asset discovery, analysis creation, strategy construction, recommendations, model execution, simulated trading, broker connectivity, exchange connectivity, autonomous execution, or real-capital orders.
- Direct frontend access to files, SQLite, Parquet, shell commands, environment variables, credentials, providers, or extensions.
- A generic Rust command or filesystem API.
- Placeholder controls that appear operational when no corresponding application capability exists.

## Terminology

- **Profile:** A versioned local OSCA working root owned and validated by the Python core.
- **Selected profile:** The profile identified by desktop preference state but not necessarily opened successfully.
- **Open profile:** A selected profile that passed compatibility, storage, and lock validation for the current session.
- **Bundled sample:** Deterministic synthetic data shipped with OSCA and imported through the canonical Python import service.
- **Application state:** A typed presentation state derived from a versioned desktop application response.
- **Unavailable:** A capability cannot currently be used and the application cannot safely infer success.

## Behavioral requirements

### D2-BR-001 — Honest shell navigation

The application must expose Home, Research, Evidence, and System as primary destinations only when D2 supplies an honest surface for them. Destinations whose capability is scheduled for later milestones must be identified as unavailable or omitted; they must not be rendered as apparently functional placeholders.

### D2-BR-002 — Responsive shell

The shell must remain usable from a 320 CSS-pixel content width through normal desktop widths. At narrow widths, navigation may collapse but all destinations and status disclosures must remain keyboard reachable and semantically labelled.

### D2-BR-003 — First-run determination

The Python application API must determine whether onboarding is required from authoritative profile and desktop-state information. The frontend must not infer first-run completion from arbitrary browser storage alone.

### D2-BR-004 — Onboarding disclosures

Before creating or opening a profile, onboarding must state that OSCA is research and simulation software, not financial advice; local data is stored on the user's machine; network use is optional and explicit; providers and credentials are not required for the sample path; recommendations are unavailable in D2; and live execution is disabled with no broker or exchange path.

### D2-BR-005 — Profile inspection

The application API must return typed profile identity, path display value, existence, compatibility, writability, lock state, storage health, and actionable findings without mutating the profile.

### D2-BR-006 — Profile creation

Profile creation must use the canonical Python initialization behavior. It must reject an unsafe non-empty target, path ambiguity, incompatible existing state, or failed initialization without leaving a partially accepted profile. The frontend may submit a path selected by a native broker dialog but must not inspect or create the path directly.

### D2-BR-007 — Profile selection and open

Selecting a profile must not claim it is open. Opening must perform authoritative compatibility, storage, and lock checks. Failure must preserve the last known safe application state and provide a structured recovery action.

### D2-BR-008 — Deterministic bundled sample import

The sample path must import the retained synthetic OHLCV fixture through the canonical Python import service. The response must identify the sample as synthetic, retain lineage, be idempotent for an equivalent accepted import, and require no network access, provider account, or credential.

### D2-BR-009 — System diagnostics

The System surface must show application version, Python package version, protocol version, profile status, storage status, sidecar status, network policy, provider readiness summary, recommendation availability, and live-execution status from typed application responses. Unknown values must be displayed as unknown or unavailable rather than guessed.

### D2-BR-010 — State model

Every asynchronous surface must explicitly support loading, ready, empty, unavailable, retryable error, blocked error, and unexpected application error states as applicable. A retry control must only be shown for operations identified as retryable by the application contract.

### D2-BR-011 — Application-level error boundary

Unexpected frontend rendering failures must be caught by an application-level error boundary that preserves the permanent safety disclosures, does not expose secrets or raw stack traces to ordinary users, and offers a safe reload or diagnostics path.

### D2-BR-012 — Accessibility foundation

All interactive elements must be operable by keyboard, have programmatic names, expose visible focus, preserve a logical tab order, and use semantic landmarks and headings. Focus must move to the main heading after primary navigation and to the error summary after a failed submitted action. Status changes must use appropriate live-region behavior without excessive announcement.

### D2-BR-013 — Motion and contrast

The UI must honor `prefers-reduced-motion`; essential state must not depend on animation. Text, controls, focus indicators, status indicators, and interactive boundaries must meet WCAG 2.2 AA contrast expectations in supported light and dark system schemes.

### D2-BR-014 — Design system reuse

D2 must define reusable design tokens and primitives for spacing, typography, color roles, borders, elevation, focus, buttons, links, fields, notices, cards, status badges, loading indicators, empty states, and error states. Product surfaces must consume semantic tokens rather than ad hoc literal styling where practical.

### D2-BR-015 — Versioned application APIs only

React may call only allowlisted, versioned desktop application methods. It must not parse CLI output or construct authoritative profile, provider, recommendation, or execution conclusions. Rust must not add domain logic or a generic filesystem/shell capability.

### D2-BR-016 — Financial and provider safety

All D2 responses and surfaces must fail closed for recommendations, live execution, provider admission, and credentials. No D2 method may submit orders, connect brokers or exchanges, acquire provider data, reveal secret values, or enable implicit networking.

### D2-BR-017 — No misleading completion

A control may be enabled only when its corresponding application capability is implemented and tested. Deferred capabilities must be clearly labelled unavailable or absent. Sample data must never be described as actual market history.

## Inputs and preconditions

- D1 application protocol `1.0` remains the negotiated baseline unless an explicit compatible revision is accepted.
- The desktop host can invoke only the allowlisted Python sidecar entrypoint.
- Profile paths originate from explicit user selection, native dialog output, or retained desktop preference state.
- Bundled sample content is shipped with the application and has documented synthetic provenance.
- Network access is disabled unless a later explicit capability enables it; D2 supplies no such capability.

## Outputs and postconditions

- A new user can complete onboarding entirely offline.
- A profile is never presented as open until Python validates it.
- Sample import produces canonical retained data and lineage or a structured failure without false success.
- The shell always exposes the product's research-only and no-live-execution boundaries.
- Later milestones can reuse the shell, tokens, primitives, state components, and typed APIs without bypassing the Python application layer.

## Invariants

- Python remains authoritative for profile, storage, import, diagnostics, provider, recommendation, and execution status.
- Frontend and Rust adapters never access SQLite or Parquet directly.
- Frontend code never receives credential values.
- Network access remains optional and inactive in D2.
- Recommendation generation and live execution remain unavailable.
- Bundled sample data remains explicitly synthetic.
- Unknown or malformed application responses fail closed.

## Failure and degradation behavior

| Failure category | Observable behavior | Recovery behavior |
|---|---|---|
| Sidecar unavailable | Shell remains visible; capability surfaces report unavailable | Retry sidecar request or open System diagnostics |
| Protocol mismatch | Application blocks affected operations and reports compatibility guidance | Install a compatible application package; no fallback parsing |
| Profile missing | Profile is not opened; an actionable finding is shown | Select another profile or create a new one |
| Profile incompatible | Profile is not mutated or opened | Use lifecycle compatibility/upgrade workflow outside D2 |
| Profile locked | Profile is not opened | Explain lock ownership/recovery without force-unlocking by default |
| Storage unwritable | Mutating actions are disabled | Choose a writable profile location or repair permissions |
| Sample already imported | Return the accepted existing identity or an explicit idempotent result | Continue to Home; do not duplicate data |
| Sample import failure | No success state; retain structured error and diagnostics link | Retry only when marked retryable |
| Malformed response | Fail closed at the typed client boundary | Show unavailable state and diagnostics path |
| Frontend rendering failure | Application error boundary replaces failed content | Safe reload or System diagnostics |

## Security and privacy

- The desktop API remains an allowlist with bounded request and response sizes.
- Path inputs are treated as untrusted and validated by Python before mutation.
- The frontend receives display-safe path strings and findings, not arbitrary directory enumeration.
- No secret values, provider tokens, environment dumps, raw stack traces, or unrestricted process output are returned.
- Tauri capabilities remain minimal. No shell plugin or broad filesystem plugin is authorized by D2.
- Diagnostics must redact sensitive values and avoid exposing machine-specific data beyond what the user explicitly selected.
- Telemetry remains disabled by default.

## Data, identity, and lineage

- Desktop preference state, if persisted, must be versioned and isolated from analytical evidence.
- Profile identity must be derived from canonical profile metadata, not a frontend-generated surrogate.
- Sample import must retain source kind `bundled-synthetic`, fixture identity/version, digest, import timestamp, producer/build identity, and resulting canonical dataset identity where supported by the existing import service.
- D2 must not create a second analytical storage format.

## Observability and operations

- Application errors use stable machine-readable codes, safe messages, retryability, and correlation/request identity.
- Diagnostics expose component status and actionable findings without secret values.
- Hosted validation results and manual acceptance evidence are retained in D2 milestone documentation.
- D1 deferred hosted validation is recorded separately from D2 feature evidence even when executed by the D2 pull request.

## Compatibility and migration

- Existing U14/D1 profiles remain readable without destructive migration.
- D2 profile creation must produce the same canonical profile structure as the supported CLI initialization path.
- Failed creation, opening, or sample import must not require manual cleanup of an accepted profile.
- Protocol additions must be backward-compatible within `1.x` or require an explicit accepted protocol decision.

## Performance and resource budgets

- Initial shell content should become interactive without waiting for nonessential diagnostics.
- Health and profile queries must be bounded and avoid scanning full datasets.
- Navigation and focus transitions must remain responsive under normal desktop workloads.
- Sample import may be asynchronous but must provide deterministic progress/state and cancellation only if the canonical import service supports safe cancellation.

## Acceptance criteria

| ID | Criterion | Verification method |
|---|---|---|
| D2-AC-001 | Clean-profile first run completes offline and reaches Home | End-to-end and manual demonstration |
| D2-AC-002 | All onboarding disclosures are presented before profile mutation | Component/accessibility test and inspection |
| D2-AC-003 | Profile inspect/create/select/open use Python application methods only | Contract, architecture, and negative tests |
| D2-AC-004 | Unsafe, missing, incompatible, locked, and unwritable profiles fail closed | Unit, integration, and recovery tests |
| D2-AC-005 | Bundled sample import is deterministic, synthetic-labelled, governed, idempotent, and offline | Integration and lineage tests |
| D2-AC-006 | Loading, empty, unavailable, retry, blocked, and app-error states are visibly distinct | Component and visual/manual evidence |
| D2-AC-007 | Keyboard-only onboarding, navigation, profile, retry, and diagnostics paths pass | Accessibility automation and manual evidence |
| D2-AC-008 | Reduced-motion and supported light/dark contrast foundations pass | Automated inspection and manual evidence |
| D2-AC-009 | Frontend has no direct filesystem, SQLite, Parquet, shell, credential, provider, or execution access | Architecture and dependency inspection |
| D2-AC-010 | Recommendations, broker/exchange connectivity, autonomous execution, and live orders remain unavailable | Security-negative and contract tests |
| D2-AC-011 | D1 deferred hosted matrix is rerun and defects are resolved or explicitly block D2 exit | GitHub Actions evidence |
| D2-AC-012 | macOS ARM64 and Linux x86-64 clean-profile manual acceptance is retained | Manual test record |

## Test strategy

- Python unit and contract tests for every new allowlisted desktop method and structured error.
- Integration tests proving profile mutations use canonical services and fail atomically.
- Golden-fixture tests for deterministic bundled synthetic sample import and lineage.
- TypeScript tests for response validation, state reduction, error handling, and navigation.
- React component tests for onboarding, shell, disclosures, focus behavior, and all state surfaces.
- Accessibility automation plus keyboard and screen-reader manual evidence.
- Rust tests preserving request bounds, sidecar framing, and the absence of generic shell/filesystem APIs.
- Architecture tests preventing frontend imports or dependencies that bypass the application API.
- Hosted Linux and macOS validation, including the deferred D1 obligation.

## Documentation requirements

- Update desktop developer bootstrap and application-contract reference.
- Add D2 manual-testing steps and validation evidence.
- Update desktop traceability and capability map.
- Record current limitations and deferred D3+ capabilities.
- Keep sample fixture provenance and research-only disclosures consistent across UI and docs.

## Open questions and deferred decisions

- Native credential-store integration is deferred to D3.
- Provider setup and acquisition are deferred to D3.
- Production charting is deferred to D5.
- Recommendation enablement remains governed by later milestones and ADR-0044/accepted recommendation decisions.
- A protocol-major change is not expected for D2; evidence requiring one must trigger explicit architecture review.
