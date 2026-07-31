# P14-P15 Requirements and Traceability Reconciliation

## Baseline

- P14 completed through PR #57 at merge commit `3aa884b4894e4f956fa93e1d70cf1930329b83b4`.
- P15 begins from that merged baseline.

## P15 requirements

| Requirement | Outcome | Implementation | Verification |
|---|---|---|---|
| REQ-0261 | Trusted local runtime extension path built on M5 contracts. | `runtime_extensions/contracts.py`, M5 extension imports | trusted-pack validation test |
| REQ-0262 | Exact identity, version, compatibility, trust, digest, permission, runtime, and output declarations. | `RuntimePackManifest` | contract construction through pack fixtures |
| REQ-0263 | Untrusted, tampered, incompatible, permission-mismatched, or invalid-path packs fail closed. | `validate_runtime_pack`, `_load_manifest` | negative validation tests |
| REQ-0264 | Explicit direct-subprocess execution with no shell and bounded resources. | `execute_runtime_pack` | disabled and successful execution tests |
| REQ-0265 | Execution evidence retains package/version, digests, permissions, logs, exit code, rationale, and findings. | `RuntimePackEvidence` and evidence retention | execution evidence test |
| REQ-0266 | Versioned installation and rollback only to installed versions. | `install_runtime_pack`, `rollback_runtime_pack` | install/rollback and missing-version tests |
| REQ-0267 | Conformance tests, manual usage, OpenSpec, traceability, exit review, and hosted Quality evidence. | P15 docs and tests | final Quality run recorded in exit review |

## Security decision

P15 permits only independently trusted local packs executed through a direct subprocess boundary. This reduces in-process blast radius but is not a complete hostile-code sandbox. Public marketplace distribution, remote discovery, untrusted execution, and implicit permission renewal remain deferred pending a separate architecture and security decision.

## Preserved boundaries

P15 does not change provider admission, production ingestion policy, secret handling, personal-server exposure controls, recommendation boundaries, broker connectivity, autonomous execution, or real-capital authorization.
