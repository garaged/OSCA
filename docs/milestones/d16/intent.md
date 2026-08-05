# D16 Intent — Desktop Extensions and Developer Experience

## Outcome
Users and contributors can inspect, validate, install, permission, execute, disable, and roll back trusted-local extensions through the desktop application with clear impact and retained execution evidence.

## Scope
Extension catalog, manifest inspection, compatibility validation, digest and trust display, permission review, staged inputs/outputs, resource limits, run evidence, disable, rollback, diagnostics, templates, and contributor documentation.

## Non-goals
Public marketplace, silent installation, hostile-code sandbox claims, unrestricted network or secret access, or extension-created live orders.

## Dependencies
D1 broker and application API, D6 evidence integration, and U14 extension contracts.

## Risks
Malicious local executables, environment leakage, permission confusion, compatibility drift, and false confidence from manifest validation.

## Exit intent
Execution remains explicitly trusted-local; permissions and impact are reviewed before execution; the broker minimizes environment and resource exposure; outputs are validated before import; disable and rollback are proven; documentation states containment limitations without ambiguity.
