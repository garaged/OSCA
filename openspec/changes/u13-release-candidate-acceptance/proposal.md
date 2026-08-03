# Change: U13 Release-Candidate Acceptance

## Why

OSCA now has a supported package lifecycle and unified operator path. The next milestone must convert those capabilities into one official, repeatable release-candidate acceptance decision.

## What changes

- define a normative 16-area acceptance matrix;
- define blocking defect severities and disposition requirements;
- create machine-readable and human-readable acceptance evidence;
- verify package artifacts, provenance, checksums, SBOM, and supported platforms;
- reconcile canonical CLI, documentation, safety boundaries, and compatibility aliases;
- select an RC version and recommend a tag only after all blocking gates pass.

## Non-goals

- publishing to a package index;
- signing artifacts without an explicit decision;
- enabling paid-provider dependence;
- enabling recommendations, live serving, brokers, autonomous execution, or real-capital orders;
- expanding analytical or model breadth except to fix an acceptance defect.

## Exit gate

All sixteen acceptance areas pass, no critical or high-severity defects remain open, medium defects are explicitly disposed, release artifacts are traceable, and the selected release-candidate tag is recommended without being created implicitly.
