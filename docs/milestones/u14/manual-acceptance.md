# U14 Contributor and Extension Acceptance

## Canonical contributor rehearsal

From a fresh checkout on macOS Apple Silicon or Linux x86-64:

```bash
uv run python scripts/contributor_check.py
```

Expected:

- locked Python environment installs;
- Ruff passes;
- strict mypy passes;
- all tests, contracts, migrations, links, and architecture checks pass;
- OpenSpec doctor and strict validation pass;
- the offline example extension returns `status: valid`;
- `compatibility_status: supported`;
- `code_imported: false`;
- `execution_enabled: false`.

## Extension validation

```bash
uv run osca extension validate \
  --manifest examples/extensions/offline-mean/osca-extension.json
```

Confirm the manifest and artifact digests are retained and that no network, credential, installation, update, or execution behavior occurs.

## Failure checks

Automated regression coverage must reject:

- prohibited capabilities;
- unknown capabilities;
- unsupported API versions;
- artifact digest mismatch;
- path traversal;
- remote installation or automatic update flags;
- malformed, missing, or incompatible manifests.

API `0.9` is accepted only as deprecated and must report migration to API `1.0` and last support in the `0.1.x` release family.

## Hosted evidence

Quality run #813 passed the implementation head with:

- core Python and architecture suite;
- trusted-local extension conformance;
- contributor rehearsal on macOS ARM64;
- contributor rehearsal on Linux x86-64;
- package lifecycle on both platforms;
- OpenSpec;
- secret scanning;
- release-candidate acceptance.

## Safety confirmation

A passing result does not authorize extension execution. Public untrusted distribution, remote installation, automatic updates, recommendations, live serving, brokers, autonomous execution, real-capital orders, remote writes, and public evidence publication remain disabled.
