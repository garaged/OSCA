# OpenSpec Integration Policy

- **Status:** Accepted pilot
- **Governing role:** Architecture authority
- **Quality approval:** Quality authority
- **Purpose:** Use OpenSpec as a bounded change-execution layer without creating a competing OSCA authority system.
- **Authoritative sources:** Engineering constitution; governed workflow; ADR-0001, ADR-0004, ADR-0005; AI contributor contract
- **Pilot change:** `m1-4-durable-diagnostic-jobs`
- **Review trigger:** M1.4 completion, OpenSpec upgrade, schema/profile change, or governance conflict
- **Last reviewed:** 2026-07-18

## Authority boundary

OpenSpec artifacts are operational views over accepted OSCA authority.

They may:

- propose a bounded change;
- organize delta scenarios, local design, and tasks;
- preserve agent-readable execution state;
- invoke validation and archive completed change history.

They must not:

- create or approve product requirements;
- allocate or redefine `REQ-NNNN` identifiers;
- accept, freeze, supersede, or replace ADRs;
- create public contract families without contract-catalog governance;
- waive security, compatibility, migration, recovery, or evidence obligations;
- declare milestone or release acceptance;
- become more authoritative than the PRD, active decisions, requirements catalog, ADRs, accepted specifications, or evidence policy.

A conflict is resolved in favor of OSCA authority and corrected in the OpenSpec artifact.

## Pinned tooling

- Package: `@fission-ai/openspec`
- Version: `1.6.0`
- Runtime: Node.js 20.19 or later
- Product runtime dependency: None
- Telemetry: Disabled with `DO_NOT_TRACK=1` or `OPENSPEC_TELEMETRY=0`

OpenSpec upgrades require release-note review, regenerated-skill diff review, strict validation, and an explicit tooling update change.

## Repository layout

- `openspec/config.yaml`: OSCA context and per-artifact guardrails.
- `openspec/changes/<change>/`: active and archived execution artifacts.
- `openspec/specs/`: synchronized OpenSpec capability views after archive; these remain non-authoritative indexes over OSCA specifications.
- `.codex/skills/openspec-*/`: pinned generated project skills reviewed with the OpenSpec version.
- `package.json` and `package-lock.json`: development-tool pin only.

Completed M0 through M1.3 artifacts are not retrofitted into OpenSpec.

## Change lifecycle

1. Link the accepted milestone intent, exact requirements, ADRs, contract families, and risk class.
2. Create the OpenSpec change.
3. Complete proposal, specs, design, and tasks.
4. Run strict validation before implementation.
5. Apply tasks in specification/test/implementation/validation/evidence order.
6. Update tasks only when evidence exists.
7. Run OSCA gates and strict OpenSpec validation.
8. Retain OSCA evidence and traceability.
9. Sync/archive only after change review and before the implementation PR merges.

## Required validation

```bash
DO_NOT_TRACK=1 npm ci
DO_NOT_TRACK=1 npm run openspec:doctor
DO_NOT_TRACK=1 npm run openspec:validate
```

OSCA implementation gates remain independently required.

## Pilot success criteria

The pilot succeeds if it:

- reduces context reconstruction across sessions;
- makes task state and spec deltas easier to review;
- introduces no contradictory authority or duplicated requirement identity;
- passes strict validation reliably;
- archives cleanly before PR merge;
- adds less maintenance cost than the execution clarity it provides.

At M1.4 closure, the authority records Adopt, Revise, or Remove. Until then OpenSpec is recommended for M1.4 only, not mandatory for every change.
