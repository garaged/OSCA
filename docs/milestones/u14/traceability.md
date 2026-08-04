# U14 Contributor and Extension Readiness Traceability

| Requirement | Implementation | Validation evidence |
|---|---|---|
| Reproducible contributor bootstrap | `CONTRIBUTING.md`, `scripts/contributor_check.py` | Hosted `contributor-rehearsal` on macOS ARM64 and Linux x86-64 |
| Strict versioned manifest | `src/osca/extension_conformance.py` | `tests/test_u14_extension_conformance.py` |
| Fail-closed non-importing validation | `validate_extension_package` | hostile capability, path, digest, and flag tests |
| Machine-readable CLI | `src/osca/extension_cli.py`, `osca extension validate` | core Quality conformance step |
| API compatibility and deprecation | supported `1.x`, deprecated `0.9`, unknown versions rejected | compatibility and deprecation tests |
| Offline example extension | `examples/extensions/offline-mean` | manifest digest and hosted conformance |
| Contribution governance | `CONTRIBUTING.md` | canonical contributor check |
| Security review | `docs/contributing/security-review.md` | PR checklist and hosted secret scan |
| Extension author guidance | `docs/contributing/extension-development.md` | documentation-link and OpenSpec validation |
| Safety preservation | literal false remote/network/update fields and forbidden capability registry | fail-closed regression tests and U14 OpenSpec |

## Trust boundary

A passing conformance result proves manifest validity, API and capability compatibility, declared provenance, and artifact integrity. It never imports extension code and never enables execution. Trusted-local execution remains governed independently.
