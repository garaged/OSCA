# OpenSpec pilot bootstrap evidence

Status: Complete  
Milestone: M1.4 preparation  
Tool: `@fission-ai/openspec` 1.6.0  
Pilot change: `m1-4-durable-diagnostic-jobs`

## Intent

Establish OpenSpec as a controlled execution layer for M1.4 without changing the authority of the M0 architecture baseline, requirements catalog, accepted ADRs, milestone specification, or retained evidence.

## Implemented

- Pinned OpenSpec 1.6.0 and committed the npm lockfile.
- Required Node.js 20.19 or later for the development toolchain.
- Disabled OpenSpec telemetry by policy.
- Added repository-specific authority and traceability guardrails.
- Added six reviewed Codex OpenSpec workflow skills.
- Created the M1.4 proposal, delta specification, design, and task plan.
- Linked the pilot from governance, milestone navigation, and the AI contributor contract.
- Added repository ignore rules for generated and local-only state.

## Validation

| Check | Result |
|---|---|
| `npm ci --ignore-scripts` | Pass; 80 packages installed from the committed lockfile |
| `npm run openspec:doctor` | Pass; repository root recognized |
| `npm run openspec:validate` | Pass; 1 change passed strict validation, 0 failed |
| `openspec status --change m1-4-durable-diagnostic-jobs` | Pass; 4 of 4 planning artifacts complete |
| Codex skill validation | Pass; 6 of 6 project skills valid |
| M1.4 task state | Accurate; 0 of 20 implementation tasks complete |

Validation ran with `DO_NOT_TRACK=1`. The committed governance policy also permits `OPENSPEC_TELEMETRY=0`.

## Findings and disposition

The OpenSpec-generated Codex skills included a `compatibility` frontmatter key that the repository skill validator does not support. The unsupported key was removed without changing workflow behavior, and all six skills then passed validation.

The active workspace protects its own `.codex` directory from generator writes. Skills were therefore generated in an isolated temporary directory, reviewed, minimally normalized, validated, and then committed to the repository.

## Conclusion

The OpenSpec pilot bootstrap is complete and the M1.4 change is apply-ready. Product implementation has not started: all 20 change tasks remain intentionally unchecked. After M1.4 validation and archival, the team must record an Adopt, Revise, or Remove decision for continued OpenSpec use.
