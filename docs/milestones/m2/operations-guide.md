# Operate M2 Governed Daily Market Data

- **Status:** Implementation-aligned draft; paid/authenticated provider production promotion is deferred beyond M2
- **Requirements:** REQ-0021–REQ-0040
- **Governing specification:** [M2 governed daily market data](../../../openspec/specs/m2-governed-daily-data/spec.md)
- **Governing decisions:** ADR-0017–ADR-0028
- **Last reviewed:** 2026-07-18

## Normative operating rules

The following rules are mandatory:

- use canonical Instrument identity; a ticker or provider symbol is only a verified time-aware mapping;
- declare an inclusive start and exclusive end date, maximum age, completeness requirement, ordered provider constraints, and idempotency key;
- treat an exact revision pin as exact—OSCA cannot silently substitute another revision;
- publish only complete daily observations into canonical storage;
- treat completed UTC dates as expected for crypto, while an unconfirmed stock weekday remains unresolved rather than automatically missing;
- repair only confirmed missing ranges and create a new immutable revision with lineage;
- preserve every accepted canonical revision throughout M2;
- preview cleanup separately from execution and revalidate current eligibility and protection at execution time;
- keep provider credentials in named vault references and provider rights in exact policy revisions;
- keep paid, authenticated, or license-sensitive provider production use disabled until its applicable account, jurisdiction, rights, endpoint, quota, and conformance evidence is accepted in a later provider-promotion change.

## Current implementation path

1. Register a canonical stock or spot-crypto pair and verify its provider mapping.
2. Submit `osca.market-data.retrieval-request` 1.0.0 through a caller holding both `market-data.retrieve` and `workflow.job.submit`.
3. Observe the durable `osca.workflow.job-run` identity and lifecycle.
4. Route through an explicit ordered provider policy. A transport/quota fallback is recorded; observations from different providers are never silently merged.
5. Normalize complete observations using exact `DECIMAL(38,18)` semantics.
6. Publish one bounded immutable Parquet object through a staging manifest, atomic object publication, and compare-and-set ready transition.
7. Resolve the exact manifest as fresh, stale, partial, corrupt, or unavailable with safe remediation.

Repair uses `osca.market-data.repair-request` 1.0.0 and requires both `market-data.repair` and `workflow.job.submit`. Its ranges must be non-empty, disjoint, confirmed gaps.

## Inspection and cleanup

Inspection groups object count, row count, bytes, and protected bytes by layer, provider, and instrument while retaining individual manifest lineage.

Cleanup follows two separate authority steps:

1. `market-data.cleanup.preview` creates a plan from current manifests, policy-derived eligibility, pins, recovery requirements, and reproducibility protection.
2. `market-data.cleanup.execute` re-runs the selection. Any changed action or accounting rejects execution. Selected objects transition to deleting, are removed, and then transition to deleted.

Canonical objects remain protected even if incorrectly included in the eligible set. A deletion interrupted after the deleting transition requires reconciliation; it must not be represented as successfully deleted.

## Provider candidate status

Twelve Data and Kraken candidate parsers implement deterministic provider-neutral response parsing and bounded injected JSON transport. The transport enforces HTTPS, an exact host, approved query keys, fixed timeout, byte limits, no redirects, no compressed responses, and an object-shaped JSON root.

This technical implementation is not licensing approval. Production configuration for paid, authenticated, or license-sensitive provider use must remain disabled until exact operating jurisdiction, account plan, intended private/non-display use, retention, backup/export rights, and API/account mode are recorded and accepted.

## Troubleshooting

| State or failure | Meaning | Safe next action |
|---|---|---|
| `stale` | A satisfying revision exceeds the declared maximum age. | Submit a refresh with the same bounded semantics. |
| `partial` | Confirmed gaps, unresolved dates, or incomplete intervals remain. | Repair confirmed gaps and resolve uncertain stock sessions. |
| `corrupt` | Stored bytes or schema fail integrity. | Quarantine the revision and repair from permitted evidence. |
| `quota_blocked` | Provider quota prevents current work. | Honor the declared retry window; do not bypass routing policy. |
| `policy_blocked` | Rights, credentials, or provider promotion are not accepted. | Correct the policy evidence; do not retain or export uncertain content. |
| cleanup plan changed | Eligibility or protection changed after preview. | Generate and review a new preview. |
| manifest remains `deleting` | Cleanup stopped between state transition and reconciliation. | Inspect object availability and reconcile; never assume deletion. |

## Current limitations

M2 does not provide intraday bars, adjusted bars, corporate actions, a complete exchange calendar, cross-provider reconciliation, automatic storage reclamation, or provider-derived repository fixtures without redistribution rights. Provider live checks are optional quarantined observations and never required CI evidence.
