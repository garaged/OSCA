# M1 Intent — Secure Walking Skeleton

- **Status:** Proposed
- **Governing role:** Product authority
- **Architecture approval:** Architecture authority
- **Purpose:** Establish a minimal, secure, observable, recoverable OSCA product that exercises every primary interface through shared application capabilities.
- **Authoritative sources:** PRD sections 16, 17, 26–29, 36, 38, and M1; D-006, D-007, D-021, D-031, D-032, D-035, D-036, D-044, D-046
- **Downstream consumers:** M1 specifications, ADRs, implementation, tests, documentation, and exit evidence
- **Review trigger:** Product-scope change, technology decision, or evidence contradicting an assumption
- **Last reviewed:** 2026-07-18

## Intent statement

Deliver a locally runnable modular-monolith walking skeleton in which the web shell, versioned API, and CLI expose one shared system-readiness capability. The slice must prove secure configuration, vault-backed secret references, durable job execution, metadata identity, structured health and telemetry, backup/restore foundations, and executable documentation without implementing M2 market-data behavior early.

## User outcome

A user can install and start OSCA locally, inspect readiness consistently through web, API, and CLI, submit and observe a durable diagnostic job, create and verify a minimal configuration/metadata backup, and follow version-matched executable documentation. Unsafe exposure, invalid configuration, missing secret-store capability, failed jobs, or invalid backup material is visible and fails safely.

## Requirements advanced

REQ-0001 through REQ-0020 in the requirements catalog define the proposed M1 allocation.

## In scope

- one shared readiness application capability;
- web, API, and CLI adapters over the same behavior;
- loopback-safe local-owner profile;
- personal-server security configuration skeleton with fail-closed validation;
- replaceable secret-vault port and local adapter;
- minimal durable job lifecycle exercised by a diagnostic job;
- stable metadata identities for job and backup records;
- structured logs, metrics, traces, audit distinction, and health aggregation;
- configuration validation with actionable diagnostics;
- minimal backup creation, integrity verification, restore preview, and isolated restore;
- version-matched installation, configuration, security, API, CLI, backup, and troubleshooting documentation;
- executable examples and retained evidence.

## Non-goals

- instruments, provider integration, market-data caching, analysis, visualization, extensions, backtesting, paper trading, ML, or LLM behavior;
- multi-user identity, synchronization, distributed deployment, or microservices;
- full disaster-recovery automation or production availability certification;
- selection of technology beyond decisions required to implement M1 safely;
- public internet exposure as a supported default.

## Success measures

- one command starts a valid local profile on loopback;
- web, API, and CLI report semantically equivalent readiness;
- invalid network/security/configuration combinations fail before serving;
- a diagnostic job survives process restart and exposes stable status;
- backup integrity and restore isolation are demonstrated;
- correlated telemetry explains success and failure without leaking secrets;
- executable documentation succeeds in the supported development environment;
- all M1 acceptance evidence is traceable to approved requirements and ADRs.

## Exit evidence

A retained evidence record links source revision, requirements, ADRs, specification criteria, structural checks, interface contract tests, security-negative tests, restart/resume evidence, backup/restore evidence, telemetry assertions, documentation execution, and remaining limitations.
