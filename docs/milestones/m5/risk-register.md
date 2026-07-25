# M5 Risk Register

| ID | Risk | Treatment |
|---|---|---|
| M5-R-001 | Unsafe extension activation grants access too early. | Activation fails closed unless trust tier and permissions are explicitly approved. |
| M5-R-002 | New extension versions reinterpret retained artifacts. | Installation records preserve exact package identity, version, digest, and dependencies. |
| M5-R-003 | Uninstall breaks reproducibility. | Impact previews identify retained references before disable or uninstall. |
| M5-R-004 | Package contracts overfit Python implementation. | Manifest records typed entry points and schemas, with runtime execution deferred. |
| M5-R-005 | M5 absorbs later strategy or ML scope. | Explicit deferred-scope register and milestone acceptance criteria keep execution out. |
