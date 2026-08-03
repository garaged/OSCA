# U13 Exit Review

- **Milestone:** U13 release-candidate acceptance
- **Status:** Candidate `0.1.0rc1` selected; final selected-version acceptance and explicit tag decision pending
- **Implementation PR:** #76
- **Recommended tag after final eligibility:** `v0.1.0rc1`

## Delivered outcome

U13 provides a normative sixteen-area acceptance matrix, machine-readable evidence index, defect severity/disposition gate, digest-addressed eligibility result, hosted supported-platform enforcement, release notes, known limitations, and explicit tag recommendation without implicit tag creation or publication.

## Blocking threshold

- Zero open critical defects.
- Zero open high defects.
- Open medium defects require workaround, owner, and target milestone.
- Any failed or blocked acceptance area denies eligibility.

## Hosted validation

The official acceptance job depends on the complete core suite and both supported package-lifecycle jobs. It builds `0.1.0rc1` candidate artifacts, verifies retained acceptance authorities, evaluates the defect registry, writes a machine-readable result, and uploads the result as workflow evidence.

## Remaining explicit decision

After the selected-version acceptance run passes, explicitly authorize or decline creation of Git tag `v0.1.0rc1`. Artifact signing and public or package-index publication remain separate future decisions.

## Safety

Recommendations, automatic model promotion, live model serving, broker or exchange connectivity, autonomous execution, real-capital orders, remote writes, and public evidence publication remain disabled. ADR-0044 remains NO-GO and P17 remains blocked.
