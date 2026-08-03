# Change: U14 Contributor and Extension Readiness

## Why

OSCA now has an accepted release candidate, but contributors and trusted-local extension authors still need one canonical development path, stable extension contracts, validation tooling, compatibility policy, and contribution governance.

## What changes

- define the supported contributor bootstrap and validation workflow;
- define stable extension manifest, capability, compatibility, and trust contracts;
- provide an independently buildable example extension and conformance fixture;
- add machine-readable extension validation and compatibility reporting;
- document review, security, provenance, licensing, and deprecation expectations;
- retain trusted-local execution only and keep public untrusted extension distribution unavailable.

## Non-goals

- creating a public extension marketplace;
- executing untrusted third-party code as a secure sandbox;
- enabling remote extension installation or automatic updates;
- enabling recommendations, live model serving, brokers, autonomous execution, or real-capital orders;
- publishing packages or artifacts without explicit authorization.

## Exit gate

A new contributor can bootstrap the repository, run all required checks, build and validate the example extension, understand compatibility and review rules, and produce a machine-readable conformance result without weakening existing safety boundaries.