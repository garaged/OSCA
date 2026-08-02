# U12 Clean-Machine Acceptance

Run this procedure independently on macOS Apple Silicon and Linux x86-64 using Python 3.13 and `uv`.

## Inputs

- Built OSCA wheel from the PR or release candidate.
- Its `SHA256SUMS`, CycloneDX SBOM, and provenance JSON.
- A disposable acceptance root.

## Procedure

1. Verify the wheel digest against `SHA256SUMS`.
2. Install the wheel with `uv tool install --force PATH_TO_WHEEL`.
3. Retain `osca version` output.
4. Create a clean profile with `osca init`.
5. Run `osca lifecycle inspect` and `osca doctor`.
6. Acquire admitted Kraken XBTUSD daily history or import a governed local dataset.
7. Run the retained research pipeline and snapshot the workspace.
8. Create a verified lifecycle backup.
9. Run `osca lifecycle upgrade` to the candidate version and retain its lifecycle-state output.
10. Confirm doctor/workspace consistency and retained evidence identifiers after upgrade.
11. Rehearse a failed upgrade using the documented acceptance fixture; confirm automatic recovery.
12. Restore the pre-upgrade backup into a separate profile and compare retained evidence identifiers and digests.
13. Start the packaged workspace on loopback and verify read-only access.

## Required retained evidence

For each platform retain:

- version report;
- checksum verification result;
- initialization result;
- pre-upgrade compatibility and doctor reports;
- populated workspace snapshot;
- backup result and backup digest;
- successful upgrade result;
- failed-upgrade recovery result;
- restored-profile compatibility and doctor reports;
- evidence identifier/digest comparison;
- packaged workspace startup result.

## Acceptance

The platform passes when installation requires no repository checkout, all lifecycle operations are structured and fail closed, accepted evidence is preserved, recovery succeeds, and every unsafe capability remains disabled.
