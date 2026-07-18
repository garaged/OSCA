# M1.7 Documentation and Operational Evidence Gap Analysis

- **Status:** Complete analysis; implementation completed and evidenced
- **Governing role:** Quality authority
- **Requirements:** REQ-0019, REQ-0020
- **Governing specification:** [M1 secure walking skeleton](../../specifications/m1-secure-walking-skeleton.md)
- **Related decisions:** ADR-0001, ADR-0004, ADR-0005, ADR-0009, ADR-0010
- **Source baseline:** `3b687466a0da3ea4dbe98fdd6827b88ceb61aee5`
- **Reviewed:** 2026-07-18

## Scope and method

This analysis compares the accepted M1 specification and evidence plan with repository documentation, retained evidence, navigation, executable tooling, and the completed M1.1–M1.6 slices. It does not redesign M0, reinterpret accepted requirements, or duplicate capability specifications.

## Completed work

| Area | Repository-backed result |
|---|---|
| Governing intent and contracts | M1 intent, scope, accepted specification, REQ-0001–REQ-0020, ADRs, and evidence plan exist and are linked from the M1 index. |
| Readiness foundation | API, CLI, web, configuration, security, telemetry, and audit behavior have implementation and retained M1.1–M1.3 evidence. |
| Durable diagnostic jobs | Focused operator guidance exists in [diagnostic-jobs.md](diagnostic-jobs.md), with retained M1.4 evidence. |
| Recovery | Focused backup and isolated-restore guidance exists in [recovery.md](recovery.md), with retained M1.5–M1.6 evidence. |
| Validation foundation | CI already runs locked environment, Ruff, strict mypy, pytest, architecture, migration, schema/link, OpenSpec, and secret-scan gates. |
| Contributor routing | Root `AGENTS.md` establishes authority order, the required workflow, validation rules, and stop conditions. |

## Partially completed work

| Area | Existing coverage | Remaining gap |
|---|---|---|
| Installation and developer setup | Package metadata, lockfile, migrations, and commands exist. | No single version-matched clean-checkout procedure states prerequisites, environment creation, database initialization, startup, and verification. |
| Configuration and security | Normative behavior and tests exist. | Operator guidance does not consolidate local versus personal-server constraints, trusted identity boundary, TLS/session prerequisites, and safe failure expectations. |
| Readiness interfaces | Interface contracts and tests exist. | No concise task-oriented page shows API, CLI, and web use from one initialized environment and explains semantic equivalence. |
| Telemetry and troubleshooting | Behavior is specified and tested. | No operator page maps safe diagnostic signals, correlation identity, audit separation, common failures, and remediation. |
| Limitations and prerequisites | Slice pages mention local limitations. | No consolidated M1 limitations section covers supported runtime, external `age` prerequisite, deployment bounds, recovery activation exclusion, and non-goals. |
| Schemas and examples | Versioned contracts and tests exist. | No documentation inventory maps examples to automated checks and contract/schema families. |
| Evidence navigation | M1.4 and M1.5–M1.6 records exist. | The evidence plan retained-slice list stops at M1.4 and omits M1.5–M1.6. No M1.7 execution record exists. |
| Traceability | Requirements and slice evidence are linked. | REQ-0019 and REQ-0020 do not yet point to a complete M1.7 documentation/evidence closure record. |

## Remaining deliverables

1. Create a bounded OpenSpec M1.7 change linked to REQ-0019, REQ-0020, the accepted specification, ADR-0005, and the evidence plan.
2. Add a single M1 operations/developer guide that routes to existing focused pages instead of repeating them.
3. Add or strengthen executable documentation checks for clean setup and representative readiness, diagnostic, and recovery examples where safe and practical.
4. Execute the documented examples in the locked environment and retain source revision, tool versions, commands, results, limitations, and integrity identity.
5. Reconcile the evidence plan, M1 index, root navigation, and traceability register.
6. Close documentation/link findings and archive the validated OpenSpec change before merge.

## Inconsistencies

- The M1 index says M1.1–M1.6 have retained evidence, while the evidence plan's retained-slice list names only through M1.4.
- Root README still describes M0.x as preparation for M1 and does not provide a direct operator/developer entrypoint for the implemented M1 product.
- The specification requires installation, developer setup, configuration, security, interfaces, jobs, recovery, telemetry, troubleshooting, limitations, schemas, and executable examples; current documentation is split across normative and focused slice pages without a complete user route.
- Evidence records use implementation-branch source checkpoints; M1.7 must distinguish historical slice evidence from validation executed against its own final source revision.

## Duplicate guidance

No blocking duplicate normative rule was found. The risk is prospective: reproducing job lifecycle or recovery invariants in a new handbook would create drift. M1.7 should:

- keep normative behavior in the accepted specification and ADRs;
- keep detailed job and recovery instructions in their existing focused pages;
- use the new guide as task-oriented routing and executable examples;
- label operational guidance as non-normative when it explains rather than mandates behavior.

## Stale references

- Add M1.5–M1.6 evidence to the evidence-plan retained-slice list.
- Replace the root README's M0.x-forward description with current M1 implementation status while retaining M0 as the authority baseline.
- Update the M1 implementation state only after M1.7 evidence exists; do not claim M1 completion before M1.8.
- Validate every existing link after navigation changes.

## Navigation improvements

- Add one “Run and operate M1” entry from the root README and M1 index.
- From that guide, route readers to the accepted specification, diagnostic-jobs guidance, recovery guidance, schemas/contracts, evidence, and limitations.
- Add the M1.7 evidence record to the M1 index, evidence plan, and traceability register.
- Keep architecture and governance indexes unchanged unless link validation identifies a genuine defect.

## Recommended implementation order

1. **Specification:** create and strictly validate the bounded OpenSpec change.
2. **Tests:** define the executable documentation/example matrix and add missing automation.
3. **Implementation:** add the consolidated task-oriented guide without duplicating normative text.
4. **Validation:** run locked setup, static checks, tests, documentation links/examples, security scan, and strict OpenSpec validation.
5. **Documentation:** reconcile root and M1 navigation plus evidence-plan references.
6. **Evidence:** retain the M1.7 record and update REQ-0019/REQ-0020 traceability.
7. **Archive:** review, synchronize, and archive OpenSpec; rerun all affected gates.

## Blocking assessment

No architecture defect or missing authority blocks M1.7. The identified M1.7 deliverables are implemented and validated in the retained M1.7 evidence. M1 completion remains pending the separate M1.8 exit review.
