# P13-P14 Requirements and Traceability Reconciliation

## Baseline

- P13 completed through PR #56 at merge commit `b22d23970be25f6425c4e5bd4d8a8ea51bb38335`.
- P14 begins from that merged baseline.

## P14 requirements

| Requirement | Outcome | Implementation | Verification |
|---|---|---|---|
| REQ-0254 | P14 delivers credible single-user personal-server operations. | `src/osca/personal_server/`, systemd templates | P14 test suite and operator quickstart |
| REQ-0255 | Operators can run governed commands, alerts, backup, and restore. | CLI and service functions | successful job, alert, backup/restore tests |
| REQ-0256 | Scope is restricted to explicit security, scheduler, alert, backup/restore, and packaging behavior. | frozen contracts and CLI commands | contract validation and focused tests |
| REQ-0257 | Deferred or unsafe operations fail closed. | enablement gates, exposure validation, endpoint/path checks | blocked job/alert/backup/restore tests |
| REQ-0258 | Automated, architecture, OpenSpec, and secret validation must pass. | Quality workflow | final hosted Quality run |
| REQ-0259 | Manual usage is executable and current. | `docs/milestones/p14/user-testing-quickstart.md` | documentation/link validation and operator review |
| REQ-0260 | Exit evidence records implementation and residual boundaries. | `docs/milestones/p14/exit-review.md` | traceability review |

## Operational dispositions

- Supported deployment: trusted single-user host.
- Default exposure: loopback-only.
- Protected remote exposure: requires TLS and authentication declarations plus operator-owned firewall, identity, and certificate controls.
- Alerts: file or HTTPS webhook only; disabled by default.
- Backup: local filesystem transport to a destination outside the source tree; the operator may mount off-device storage there.
- Restore: isolated staging and path validation; active destination replacement requires explicit overwrite.
- Packaging: systemd service/timer examples; no managed cloud or Kubernetes provisioning.

## Preserved boundaries

P14 does not authorize multi-tenant SaaS, anonymous public access, remote arbitrary command submission, secrets in portable configuration, provider scope expansion, recommendations, broker/exchange connections, autonomous trading, or real-capital orders.
