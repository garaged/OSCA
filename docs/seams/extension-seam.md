# Extension Seam

- **Status:** Draft
- **Owner:** Extension governance capability
- **Purpose:** Allow independently distributed capabilities while preserving compatibility, permissions, provenance, reproducibility, and failure isolation.

## Contract groups

- package manifest and integrity identity;
- compatibility declaration;
- capability entry points and schemas;
- dependencies and environment lock;
- permission and resource declarations;
- installation, trust, activation, update, disable, and uninstall lifecycle;
- conformance and diagnostics;
- impact preview and retained-artifact references.

## Mandatory behavior

- Installation and activation are separate.
- Packages are pinned by exact identity, version, source, digest, resolved dependencies, and granted permissions.
- Extensions import only approved public contracts.
- Extensions do not mutate canonical data or access private persistence.
- Credentials are granted as named capabilities, never raw vault access.
- Permission increases require renewed approval.
- Updating an extension does not reinterpret retained analyses or artifacts.
- Disable and uninstall operations preview reproducibility and dependency impact.
- Trust tier and signature establish provenance and integrity, not unconditional safety.
- Failures return structured diagnostics and cannot corrupt unrelated workflows.

## Conformance evidence

A common suite covers manifest validation, compatibility, schema behavior, permission denial, network and filesystem restrictions, deterministic or seed claims, resource limits, failure isolation, provenance, update impact, and uninstall safety.