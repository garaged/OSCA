# M5 Acceptance Criteria

| ID | Criterion |
|---|---|
| M5-AC-001 | Extension manifests carry stable package identity, publisher identity, semantic version, category, entry points, compatibility, schemas, supported scopes, permissions, integrity, license, and provenance. |
| M5-AC-002 | Manifest validation rejects missing entry points, empty compatibility, duplicate permissions, duplicate dependencies, and missing integrity digest. |
| M5-AC-003 | Installation records preserve exact package identity, version, source, integrity digest, resolved dependencies, granted permissions, and activation state. |
| M5-AC-004 | Activation is explicit and fails closed for untrusted or quarantined trust tiers. |
| M5-AC-005 | Permission changes require renewed approval before activation. |
| M5-AC-006 | Disable and uninstall previews identify impacted retained analyses, artifacts, projects, reports, and extension dependencies. |
| M5-AC-007 | M4 research contracts remain compatible and are not reinterpreted by newer extension versions. |
| M5-AC-008 | Documentation, OpenSpec, traceability, ADR, tests, and retained evidence are updated before M5 exit. |
