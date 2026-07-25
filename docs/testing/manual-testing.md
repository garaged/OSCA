# Manual Testing and Usage

- **Status:** Active from M8
- **First covered milestone:** M8 F3 paper evaluation and automation foundation
- **Audience:** Maintainers and early operators
- **Purpose:** Keep a small manual smoke-test checklist for behavior that is easier to validate through real usage than through automated checks alone.

## Governance

M8 is the first OSCA milestone that documents manual tests and usage flows.

Every later milestone specification must review this document when the milestone adds, removes, or changes user-visible or operator-visible behavior. The milestone must either update this document or explicitly state why no manual testing or usage change is required.

Manual checks do not replace automated tests, OpenSpec validation, architecture checks, or hosted Quality. They are a lightweight reality check for setup, CLI/admin usage, persisted metadata, failure handling, and milestone boundaries.

## When to Run

Run this checklist after merging a milestone that changes any of these surfaces:

- CLI or admin commands.
- Local storage, migrations, or metadata persistence.
- Provider configuration or data ingestion.
- Backtesting, event-driven validation, or paper evaluation flows.
- Notifications, schedules, recovery, or operator controls.
- Documentation that changes setup or usage expectations.

For M8, run the checklist after PR #29 is merged and before starting broad product-style testing.

## Preparation

1. Start from a clean checkout of main after the milestone merge.
2. Install the project using the repository's documented development setup.
3. Use local, non-production configuration.
4. Do not configure real-capital broker or exchange execution credentials.
5. Use disposable local metadata files for any SQLite-backed checks.

## M8 Smoke Checklist

| Area | Manual check | Expected result |
|---|---|---|
| Repository health | Run the documented hosted/local Quality-equivalent checks available to the operator. | Checks pass or failures are understood before usage testing continues. |
| CLI discovery | Inspect available CLI/admin commands. | Existing commands remain discoverable and no M8 command implies live trading. |
| Paper account model | Create or inspect a paper account through the available developer/operator surface. | The account has stable identity, base currency, lifecycle status, and no live-execution identity. |
| Candidate gate | Try paper evaluation with an approved candidate and with a blocked/unapproved candidate. | Approved candidates can proceed; blocked or unapproved candidates fail closed. |
| Health controls | Exercise blocked data or operational health state where supported. | Paper processing is blocked when health findings are errors or blocked states. |
| Pause and kill switch | Inspect pause and kill-switch behavior where supported. | Controls are explicit and block paper processing without affecting live execution, which is absent. |
| Metadata persistence | Persist and query paper metadata using a disposable SQLite file. | Records round trip by paper account or paper run identity. |
| Schedules and recovery | Inspect schedule and missed-run recovery decisions. | Recovery does not replay unsafe work and remains blocked when required evidence is missing. |
| Notifications | Generate or inspect paper notification/digest records. | Notifications remain local evidence; external delivery adapters do not send messages unless explicitly implemented and enabled in a later milestone. |
| Deferred boundaries | Review M8 docs and CLI/help text for live execution, ML, LLM, F4 fidelity, and provider promotion. | Deferred scope remains visible and no user path suggests those capabilities are production-ready. |

## Usage Notes

At M8, OSCA is still a governed engineering foundation. Manual testing should focus on operational smoke checks and safety boundaries, not strategy profitability, broad UX polish, or production trading readiness.

Use this document as the durable baseline for future milestones. When M9 or later introduces new usage surfaces, append focused checks instead of rewriting historical milestone coverage.

## M9 Smoke Checklist

| Area | Manual check | Expected result |
|---|---|---|
| ML scope boundary | Review M9 CLI/help/docs and available developer surfaces. | ML lifecycle is presented as governed evidence; no path suggests live trading or automatic promotion. |
| Feature registry | Create or inspect feature definitions where supported. | Features preserve source dataset, transformation, value type, and point-in-time safety. |
| Label registry | Create or inspect label definitions where supported. | Labels preserve objective, horizon, source dataset, and leakage-check evidence. |
| Evaluation report | Inspect a model evaluation report where supported. | Holdout metrics and calibration methodology are visible before promotion. |
| Promotion gate | Try promotion with passing and blocked evidence where supported. | Passing evidence can approve event validation; error findings or missed thresholds fail closed. |
| Drift monitoring | Inspect monitoring reports where supported. | Drift threshold breaches are visible as degraded or blocked, not silently healthy. |
| Retraining boundary | Review retraining docs and records where supported. | Retraining creates evidence but does not automatically promote a model. |

## M10 Smoke Checklist

| Area | Manual check | Expected result |
|---|---|---|
| LLM scope boundary | Review M10 CLI/help/docs and available developer surfaces. | LLM behavior is presented as governed lifecycle evidence; no path suggests provider calls, generated recommendations, live trading, or automatic state changes are ready. |
| Provider route evidence | Inspect an LLM route decision where supported. | The decision preserves exact provider/model identity, capability, privacy class, budget, and rationale. |
| Tool boundary | Inspect registered LLM tool definitions where supported. | Tools declare read or state-changing mode, permission scope, and live-order prohibition. |
| Prompt and context versioning | Inspect prompt template and context policy records where supported. | Records preserve version identity, selected project context, approved references, and no unrelated project mixing. |
| Budget and privacy gates | Try route evaluation with over-budget or sensitive-disclosure inputs where supported. | Evaluation fails closed before any provider call. |
| Evaluation evidence | Inspect LLM evaluation records where supported. | Grounding, structured-output validity, boundary behavior, cost, and latency findings are visible as evidence. |


## M11 Smoke Checklist

| Area | Manual check | Expected result |
|---|---|---|
| Analytical breadth boundary | Review M11 CLI/help/docs and available developer surfaces. | M11 is presented as governed analytical-pack metadata and evidence, not as complete runtime analytics engines. |
| Pack manifest review | Inspect a fundamental, macro, events, news, crypto, portfolio, visualization, or synthesis pack manifest where supported. | Pack family, version, data requirements, methodology, assumptions, limitations, and documentation are visible. |
| Validation failure | Try pack validation with missing methodology documentation where supported. | Validation fails closed with a blocking finding. |
| Evidence synthesis | Inspect cross-family synthesis evidence where supported. | Supporting and contradicting evidence references remain visible. |
| Method comparison | Try selecting a preferred method outside the compared set where supported. | The comparison is blocked instead of accepting an unrelated winner. |
| Outcome calibration | Inspect expected-versus-realized outcome records where supported. | Calibration status and error metric are retained. |
| Portfolio scenario | Inspect portfolio scenario evidence where supported. | Scenario reports remain analytical evidence and do not imply order authority. |
| Visualization metadata | Inspect visualization pack metadata where supported. | Accessible summaries and export metadata are required. |


## M12 Smoke Checklist

| Area | Manual check | Expected result |
|---|---|---|
| Release-readiness boundary | Review M12 CLI/help/docs and available developer surfaces. | M12 is presented as governed operational metadata and evidence, not production backup delivery, restore execution, scheduler execution, or live trading. |
| Backup manifest review | Inspect a lightweight, standard, or archival backup manifest where supported. | Profile, recovery point, encryption, integrity digest, recovery classes, exclusions, off-device intent, and secret-reference-only behavior are visible. |
| Restore verification | Inspect restore verification evidence where supported. | Verification uses an isolated target and blocks when integrity, compatibility, or journal reconciliation fails. |
| DR exercise evidence | Inspect disaster-recovery exercise records where supported. | Scenario, objectives, duration, linked restore verification, findings, and status are retained. |
| Health finding | Inspect a degraded or blocked health finding where supported. | Impact, remediation guidance, correlation identity, and findings are visible. |
| Alert policy | Inspect alert policy metadata where supported. | Dedupe, escalation, and destination metadata are present, while external delivery remains disabled. |
| Missed workflow safety | Try a financially meaningful missed-run record without approval where supported. | Validation fails closed instead of scheduling automatic replay. |
| Risk control boundary | Try approving a breached strict risk control where supported. | The decision is rejected or validation fails closed. |
| Persistence scope | Persist and query operations metadata using a disposable SQLite file. | Records round trip by component, workflow, or policy identity. |
