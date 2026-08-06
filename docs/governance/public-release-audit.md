# Public Release Audit

Status: Public baseline accepted; repository security reporting and secret protections enabled.

Original audit date: 2026-08-05  
Reconciled: 2026-08-05

## Scope

This audit covers the repository tree and available GitHub metadata for:

- secrets and credentials;
- private URLs and machine-specific paths;
- personal information in files and Git metadata;
- fixture and dataset provenance;
- generated artifacts and local state;
- project and third-party licensing boundaries;
- public vulnerability reporting.

This document records a bounded repository-host audit. It does not replace a full local scan of every clone or unreachable Git object retained outside the repository host.

## Public baseline disposition

The repository owner completed the public-release and repository-security actions and explicitly accepted the remaining personal Git identity exposure:

- the repository is public;
- history was rewritten to remove the Oracle work address from reachable commit metadata;
- obsolete local and remote branches were removed;
- `main` is the retained baseline branch;
- `garaged@gmail.com` exposure is explicitly accepted by the repository owner;
- Apache License 2.0, NOTICE, package licensing, synthetic fixture provenance, and the security policy are merged;
- GitHub Actions are enabled;
- private vulnerability reporting is enabled;
- repository secret-protection settings were enabled by the repository owner;
- hosted Quality full-history secret scanning passes on the rewritten baseline and D2 branch history available to the workflow.

The connected GitHub metadata for the rewritten D1 commit contains no Oracle `Co-authored-by` trailer. Historical search indexes or unreachable objects may take time to disappear from external caches and are not treated as reachable repository history.

## Findings

### License and attribution

- Apache License 2.0 is present at the repository root.
- NOTICE separates original OSCA material from third-party dependency terms.
- Python, Rust, and desktop package metadata declare `Apache-2.0`.
- Release SBOMs remain the build-specific dependency inventory.

Disposition: accepted.

### Current-tree secrets and local state

- `.gitignore` excludes `.env`, `.env.*`, `.osca/`, databases, virtual environments, dependency directories, and build outputs.
- Repository secret-protection settings are enabled by the owner.
- Hosted Quality uses a full-history checkout for its `gitleaks` action and passes on the rewritten baseline and active D2 work.
- The connected GitHub integration does not have permission to enumerate secret-scanning alerts or the exact enabled subfeatures, so push protection, validity checks, and non-provider pattern settings must not be inferred beyond the owner-confirmed configuration.
- No local profile, generated evidence, provider credential, or restricted provider payload is intentionally tracked.

Disposition: accepted for the current hosted baseline. GitHub-native protection and independent full-history scanning are complementary controls. Maintainers must continue running full-history scans after any future history rewrite or imported repository history.

### Personal information

- Reachable commits expose the accepted personal address `garaged@gmail.com`.
- The repository owner explicitly accepts that exposure.
- The Oracle work address was removed from reachable commit metadata during the history rewrite.

Disposition: accepted by repository owner. Future identity changes remain an owner preference and are not a release blocker unless a work or private address is introduced unintentionally.

### Fixtures and datasets

- `tests/fixtures/local_ohlcv/aapl_backtest_daily.csv` and the D2 bundled sample are deterministic synthetic OHLCV data.
- Their round-number sequences, constant volume, and constructed timestamps are not copied market history.
- `AAPL` is a scenario label only. D2 uses `AAPL-SYNTHETIC` in the retained imported dataset identity.
- No provider response, credential-bearing export, user profile, or generated evidence may be committed.

Disposition: accepted with retained provenance and synthetic labelling.

### Generated artifacts

- The current tree does not intentionally include local profiles, databases, dependency directories, Python build output, or desktop target output.
- Release binaries, desktop packages, checksums, provenance, and SBOMs are produced from identified source commits and retained as workflow/release artifacts rather than source files unless explicitly governed otherwise.

Disposition: accepted, subject to clean-tree and artifact provenance checks for each release.

### Security reporting

- `.github/SECURITY.md` directs reporters to GitHub private vulnerability reporting.
- The GitHub repository API reports private vulnerability reporting as enabled.
- The fallback through the repository owner's GitHub profile remains documented for service availability or access problems.

Disposition: accepted and operational.

## Maintainer verification gates

Run from a fresh local clone with all reachable refs fetched when preparing a release or after any history rewrite:

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

Any real credential found in any historical commit must be revoked or rotated first. Removing it from the current tree is insufficient. A future history rewrite must invalidate obsolete clones, branches, and tags as appropriate.

## Ongoing public-release invariants

- Apache-2.0 licensing and NOTICE remain present and accurate.
- GitHub-native secret protection remains enabled.
- Hosted full-history secret scanning remains passing.
- Private vulnerability reporting remains enabled and accurately documented.
- Public author and committer identities are intentional.
- Local profiles, generated evidence, credentials, and restricted provider data remain untracked.
- Synthetic fixtures remain clearly identified as synthetic.
- Release artifacts remain traceable to an accepted source commit.
