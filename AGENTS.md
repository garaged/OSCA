# AGENTS.md

## Purpose

This file is the repository entrypoint for human and AI contributors. It routes work to OSCA's authoritative sources and defines uniform execution behavior. It does not replace the PRD, requirements, ADRs, specifications, governance documents, or retained evidence.

These instructions apply to the entire repository. A more specific `AGENTS.md` may add local constraints but cannot weaken or contradict this file or governing authority.

## Authority order

When sources conflict, stop and resolve the conflict in this order:

1. approved product requirements and decision log;
2. active numbered requirements in the requirements catalog;
3. Frozen or Accepted ADRs;
4. accepted milestone intent and normative specification;
5. governance and engineering policies;
6. accepted public contracts and canonical OpenSpec capability views;
7. implementation plans, OpenSpec change artifacts, guidance, and examples;
8. code comments and local conventions.

Never silently reinterpret a higher-authority source. Record genuine defects and obtain the appropriate authority decision before changing normative meaning.

Start with:

- `ARCHITECTURE_STATUS.md`
- `docs/product-requirements.md`
- `docs/governance/requirements-catalog.md`
- `docs/governance/traceability-register.md`
- `docs/decisions/README.md`
- `docs/specifications/`
- `engineering/constitution.md`
- `engineering/ai-contributor-contract.md`

## Required workflow

Every implementation change follows:

```text
Intent → Requirements → Architecture → Specification → Validation → Evidence
```

Before editing:

1. read the applicable intent, exact `REQ-NNNN` entries, ADRs, specification, and existing evidence;
2. inspect current repository organization and reuse existing guidance;
3. identify the smallest remaining deliverable;
4. confirm ownership, public contracts, risk class, migration impact, and required gates;
5. distinguish normative rules from non-normative guidance.

During implementation:

- preserve capability boundaries and persistence ownership;
- use public seams across capabilities; never import another capability's private infrastructure;
- keep public contracts typed, versioned, deterministic, and traceable;
- make security, failure, compatibility, recovery, and observability behavior explicit;
- add specification-first and failure-oriented tests;
- update task state only after supporting implementation or evidence exists;
- update indexes and navigation when artifacts move or are added;
- avoid unrelated cleanup, architecture redesign, and duplicate documentation.

## M0 and architectural integrity

M0 and its Frozen Tier-1 ADRs are the authoritative architecture baseline. Do not redesign or recreate them. A change to Frozen or Accepted architecture requires the governed ADR and architecture-evolution process.

Use the architecture registry and validation guidance under `engineering/` and `docs/validation/`. If implementation pressure conflicts with the baseline, pause and escalate the conflict rather than introducing drift.

## OpenSpec

OpenSpec is an execution layer, not an authority system. Follow `docs/governance/openspec-integration.md`.

For applicable governed changes:

- link exact requirements, ADRs, contracts, risk, and authoritative specification;
- validate planning artifacts strictly before implementation;
- apply tasks in specification/test/implementation/validation/documentation/evidence order;
- keep OSCA gates and retained evidence independent of OpenSpec validation;
- sync and archive only after implementation review;
- replace generated placeholders and repair navigation after archive.

Do not retrofit completed history or use OpenSpec to approve requirements, ADRs, exceptions, milestone acceptance, or contract families.

## Validation and evidence

Validation must be proportional to the risk class and include all gates required by ADR-0005 and the applicable evidence plan. At minimum for Python implementation changes:

```bash
uv sync --locked
uv run ruff check .
uv run mypy
uv run pytest
```

Run applicable migration, architecture-boundary, schema, compatibility, security, adapter, documentation, and OpenSpec gates. Do not claim a gate passed unless it was executed successfully against the reported source revision.

Retain evidence under the applicable `evidence/<milestone>/` directory with source identity, tools, results, limitations, residual risks, and deferred work. CI evidence supplements but does not erase repository evidence.

## Stop conditions

Pause and report a blocker when:

- authoritative sources conflict or required normative behavior is unspecified;
- a required requirement, ADR, contract, migration, security decision, or evidence plan is missing;
- implementation would cross ownership boundaries or broaden scope materially;
- required validation cannot run or fails;
- generated artifacts contain placeholders or stale links;
- review discovers an unsupported completion claim.

Never mark tasks complete, approve a PR, or merge while a blocking finding remains.

## Pull requests

PRs must state scope, governing requirements and ADRs, validation performed, evidence links, residual risks, and deferred work. Review the complete diff, unresolved threads, approvals, mergeability, and required checks.

A merge is allowed only when:

- the branch is current with its base;
- no blocking review finding remains;
- required checks and evidence pass;
- normative documentation, contracts, navigation, traceability, and archives match the implementation;
- the expected head revision is verified at merge time.
