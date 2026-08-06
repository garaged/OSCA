# Public Release Audit

Status: Conditional no-go until the required local history checks are completed and the repository owner accepts the public Git identity exposure.

Audit date: 2026-08-05

## Scope

This audit covers the repository tree and available GitHub metadata for:

- secrets and credentials;
- private URLs and machine-specific paths;
- personal information in files and Git metadata;
- fixture and dataset provenance;
- generated artifacts and local state;
- project and third-party licensing boundaries;
- public vulnerability reporting.

This document records a bounded repository-host audit. It does not replace a full local scan of every reachable Git object.

## Findings

### License and attribution

- Apache License 2.0 is present at the repository root.
- NOTICE separates original OSCA material from third-party dependency terms.
- Python, Rust, and desktop package metadata declare `Apache-2.0`.
- Release SBOMs remain the build-specific dependency inventory.

Disposition: ready after the licensing pull request is merged.

### Current-tree secrets and local state

- `.gitignore` excludes `.env`, `.env.*`, `.osca/`, databases, virtual environments, dependency directories, and build outputs.
- Bounded GitHub code searches found no AWS access-key prefix or private-key marker, but GitHub marked those searches incomplete.
- The repository secret-scanning alerts endpoint was unavailable to this audit, so absence of alerts was not established.

Disposition: full-history local secret scanning is required before changing repository visibility.

### Personal information

- Git commits expose the author and committer email `garaged@gmail.com`.
- This address will become public with repository history unless the owner accepts that exposure or rewrites the history before publication.

Disposition: explicit owner decision required. Future commits should use a GitHub noreply address when privacy is preferred.

### Fixtures and datasets

- `tests/fixtures/local_ohlcv/aapl_backtest_daily.csv` is deterministic synthetic OHLCV data. Its round-number sequence, constant volume, and constructed timestamps are not copied market history.
- The fixture uses `AAPL` only as a scenario label and must not be described as actual Apple market data.
- No provider response, credential-bearing export, user profile, or generated evidence should be committed.

Disposition: ready with the fixture provenance notice added in this pull request.

### Generated artifacts

- The current tree does not intentionally include local profiles, databases, dependency directories, Python build output, or desktop target output.
- Release binaries, checksums, provenance, and SBOMs must be produced from an accepted source commit and published separately from source unless deliberately retained.

Disposition: ready, subject to a clean-tree check immediately before publication.

### Security reporting

- No repository security policy existed at the time of audit.
- A `.github/SECURITY.md` policy is added by this pull request and directs vulnerability reports to GitHub private vulnerability reporting rather than public issues.

Disposition: confirm private vulnerability reporting is enabled in repository settings before publication.

## Required local gates

Run from a fresh local clone with all remote refs fetched:

```bash
git fetch --all --tags --prune

# Full reachable-history secret scan.
gitleaks git --redact --log-opts="--all"

# Review public author and committer identities.
git log --all --format='%an <%ae>%n%cn <%ce>' | sort -u

# Review historically committed sensitive file names.
git log --all --name-only --pretty=format: -- \
  '*.env' '.env*' '*.pem' '*.key' '*.p12' '*.pfx' '*.jks' \
  | sed '/^$/d' | sort -u

# Review machine-specific paths and private URL indicators in the current tree.
git grep -nE '(/Users/|/home/[^/$]|file://|localhost:[0-9]+|127\.0\.0\.1:[0-9]+)' -- . \
  ':!docs/governance/public-release-audit.md'

# Confirm no ignored local or generated content is tracked.
git ls-files -ci --exclude-standard

git status --short
git diff --check
```

Any real credential found in any historical commit must be revoked or rotated first. Removing it from the current tree is insufficient. Decide separately whether history rewriting is necessary, then invalidate old clones and tags as appropriate.

## Public visibility decision

The repository is ready to become public only when all of the following are true:

- the Apache-2.0 licensing pull request is merged;
- the full-history `gitleaks` scan passes or every finding is resolved;
- the public exposure of historical Git identities is explicitly accepted or remediated;
- private vulnerability reporting is enabled;
- the final tree is clean and contains no local profiles, generated evidence, credentials, or restricted provider data.

Changing visibility is a separate repository-owner action and is not authorized by this audit.
