# Contributing to OSCA

OSCA uses intent-driven, specification-driven, and test-driven development. Contributions must preserve local-first operation, retained evidence, provider policy, and fail-closed safety boundaries.

## Supported contributor environments

- macOS Apple Silicon
- Linux x86-64
- Python 3.13
- `uv`
- Node.js 22 and npm for OpenSpec validation

## Bootstrap

From a fresh checkout:

```bash
uv sync --locked
npm ci --ignore-scripts
```

Run the complete local contribution gate:

```bash
uv run python scripts/contributor_check.py
```

This command runs the locked Python setup, Ruff, strict mypy, tests and architecture checks, OpenSpec validation, and trusted-local extension conformance.

## Change authority

Every coherent change must identify:

- the governing milestone, specification, issue, or accepted decision;
- affected contracts and safety boundaries;
- tests proving the intended behavior and failure behavior;
- documentation and traceability updates;
- migration, compatibility, and deprecation consequences.

Do not introduce recommendations, automatic model promotion, live model serving, broker or exchange order connectivity, autonomous execution, real-capital orders, remote writes, or public evidence publication.

## Pull-request checklist

- [ ] Scope is coherent and linked to an accepted authority.
- [ ] New behavior has deterministic tests, including failure cases.
- [ ] `uv run python scripts/contributor_check.py` passes.
- [ ] Public interfaces and schemas are versioned or compatibility-assessed.
- [ ] Documentation, manual testing, and traceability are updated.
- [ ] Provider licensing, provenance, and redistribution constraints are retained.
- [ ] No secrets, credentials, private datasets, or generated evidence are committed.
- [ ] Security-sensitive changes include an explicit threat and trust review.

## Extension contributions

Extension packages are trusted-local only. Validation reads JSON and artifact bytes but does not import or execute extension code. A contribution must include:

- `osca-extension.json` using the supported manifest family and version;
- explicit API version and capabilities;
- HTTPS source repository and full source commit;
- SPDX license identifier;
- SHA-256 for every packaged artifact;
- offline deterministic conformance tests;
- no remote installation or automatic update behavior.

Validate an extension package with:

```bash
uv run osca extension validate --manifest path/to/osca-extension.json
```

A valid manifest is not authorization to execute hostile or unreviewed code. Trusted-local acceptance remains a human governance decision.

## Compatibility and deprecation

Breaking extension API changes require a new major API version, migration guidance, an accepted decision, and a documented support window. Deprecations must be announced before removal and must retain deterministic compatibility tests during the support window.

## Licensing and provenance

Contributors must have the right to submit all code, fixtures, datasets, and documentation. Third-party material must retain its license and provenance. Market data must not be committed unless redistribution is explicitly permitted.
