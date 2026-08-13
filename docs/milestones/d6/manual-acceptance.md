# D6 Manual Acceptance — Research Projects, Saved Workspaces, and Integrated Evidence

Run this procedure from a clean profile on each supported D6 platform: macOS ARM64 and Linux x86-64. Use bundled sample data, governed local data, or retained D5 evidence so the core path requires no paid provider, network access, or external account.

Record only generic PASS/FAIL evidence in the repository. Do not commit private filesystem paths, credentials, provider account details, or personal data.

## 1. Launch and safety boundary

1. Build and launch the packaged native desktop application.
2. Open or create a clean profile.
3. Enter the Projects area.
4. Confirm the surface identifies itself as research organization/evidence management only and provides no recommendation, broker, order, notebook-execution, or real-capital action.
5. Keep the local/sample path offline and confirm no unexpected provider request occurs.

Expected: Projects opens without paid services, network access, or a separately started development server.

## 2. Project lifecycle

1. Create a project with a clear name and objective.
2. Inspect its stable identity, status, creation metadata, and update metadata.
3. Rename or update the objective.
4. Archive the project and confirm it leaves the default active list while remaining recoverable.
5. Restore the project.
6. Clone the project and confirm the clone has a distinct identity and clone provenance.

Expected: lifecycle changes are explicit, durable, profile-scoped, and reflected in the timeline.

## 3. Pins and broken references

1. Pin at least one canonical asset or watchlist.
2. Pin a governed dataset revision or retained local-data import.
3. Pin a D5 Workbench view or full-resolution export when available.
4. Restart the application and confirm pins remain.
5. Exercise a broken or unavailable reference if the test fixture exposes one.

Expected: pins preserve typed source identity and degraded state; missing references are disclosed rather than silently removed or replaced.

## 4. Notes

1. Add a user note to the project.
2. Edit the note.
3. Reference a pinned item from the note if supported.
4. Confirm the UI labels the content as user-authored note material, not generated evidence or a recommendation.

Expected: notes are durable, bounded, clearly labeled, and never treated as authoritative analytical output.

## 5. Timeline

1. Inspect timeline entries after project creation, metadata update, pin changes, note changes, archive/restore, clone, and export.
2. Confirm event ordering is deterministic after restart.
3. Confirm failed validation does not create a misleading successful event.

Expected: timeline records an auditable sequence of project events.

## 6. Saved project workspaces

1. Configure a project workspace with visible sections, selected pins, timeline filters, and a D5 Workbench view reference when available.
2. Save the workspace.
3. Restart the application and restore the workspace.
4. Confirm underlying datasets, Workbench views, and evidence are not mutated by restoring the workspace.

Expected: workspace restore is declarative and reproducible.

## 7. Manifest export

1. Export the project manifest.
2. Confirm metadata includes schema/version, producer, export timestamp, project identity, lifecycle state, pins, notes, timeline, workspaces, and degraded-link disclosures.
3. Confirm notes are labeled as user-authored.
4. Confirm the export is a thin manifest and does not unexpectedly bundle provider datasets or private profile paths.

Expected: export is reproducible evidence, not an uncontrolled data package.

## 8. Profile isolation and ownership

1. Open a second window or process against the same profile using the established D4/D5 ownership procedure.
2. Attempt a project mutation from the non-owner.
3. Confirm the mutation fails visibly.
4. Open a different clean profile and confirm the first profile's projects are absent.
5. Release ownership and confirm a subsequent owner can mutate the project.

Expected: project state is profile-scoped and protected by the existing desktop ownership boundary.

## 9. Accessibility and responsive layouts

Verify all of the following:

- keyboard-only operation for project navigation, lifecycle actions, pins, notes, workspaces, timeline, and export;
- visible focus and no keyboard trap;
- screen-reader labels for project status, pins, notes, timeline events, validation errors, and export results;
- light and dark appearance where platform/application settings support them;
- forced/high-contrast mode retains controls, focus, state, and timeline meaning;
- reduced-motion mode removes nonessential animated transitions;
- state differences are not communicated by color alone;
- narrow 320 CSS-pixel layout retains essential controls without inaccessible horizontal loss;
- intermediate 680 CSS-pixel and normal desktop layouts remain usable.

## 10. Performance and packaging

1. Launch the packaged app directly.
2. Load a typical project and confirm it becomes usable within the D6 three-second target on acceptance hardware.
3. Exercise a project with many pins/timeline entries and confirm ordinary interactions remain responsive.
4. Start a manifest export and confirm longer work surfaces progress or meaningful busy/error state rather than freezing the desktop UI.

Expected: typical local project operations are responsive, and larger projects remain bounded by pagination, filtering, or explicit export behavior.

## Acceptance result

Record a platform PASS only when all applicable sections pass. Any hidden mutable reference, lost evidence, profile-isolation failure, misleading note/evidence treatment, unexpected network/provider use, accessibility blocker, brokerage/execution path, or recurring unacceptable UI stall blocks D6 exit.
