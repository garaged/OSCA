# Trusted-Local Extension Development

OSCA U14 supports extension package validation and contributor conformance. It does not provide a public marketplace, remote installer, automatic updater, or hostile-code sandbox.

## Package layout

```text
my-extension/
├── osca-extension.json
└── extension.py
```

The manifest is validated before any code import. Validation is JSON-only and verifies every declared artifact digest.

## Manifest contract

Required fields:

- `family`: `osca.extension-manifest`
- `manifest_version`: `1.0.0`
- `extension_id`: lowercase dotted or dashed identifier
- `extension_version`: explicit semantic version
- `api_version`: currently major version `1`
- `entry_point`: `module.path:callable`
- `trust`: `trusted-local`
- `license_spdx`: SPDX license identifier
- `source_repository`: HTTPS repository URL
- `source_commit`: full lowercase 40-character Git SHA
- `capabilities`: unique declared capabilities
- `artifacts`: relative path and SHA-256 for every packaged artifact
- `network_access`: `false`
- `remote_installation`: `false`
- `automatic_updates`: `false`

Supported U14 capabilities:

- `analysis.read`
- `dataset.read`
- `evidence.write-local`
- `metrics.compute`

Capabilities involving recommendations, brokers, exchange orders, live serving, real capital, or remote writes are rejected.

## Validation

```bash
uv run osca extension validate \
  --manifest examples/extensions/offline-mean/osca-extension.json
```

The command returns machine-readable JSON and exits nonzero when the package is invalid. A successful result explicitly reports:

- verified manifest digest;
- extension identity and API version;
- declared capabilities;
- verified artifact paths;
- `code_imported: false`;
- `execution_enabled: false`.

## Trust decision

Conformance proves structural validity, declared capability compatibility, provenance fields, and artifact integrity. It does not prove that code is safe. Execution remains limited to independently reviewed trusted-local packages accepted through project governance.

## Compatibility

API major `1` is the current supported extension contract. A future breaking API change requires a new major version, migration guidance, an accepted decision, and a documented deprecation window. Unknown API majors fail closed.

## Example

`examples/extensions/offline-mean` is an offline deterministic example. It has no network, credential, provider, recommendation, or execution capability and can be validated without importing its Python module.
