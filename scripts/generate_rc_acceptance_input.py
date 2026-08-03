from __future__ import annotations

import argparse
import json
from pathlib import Path

from osca.release_acceptance import ACCEPTANCE_AREAS

COMMON_HOSTED = (".github/workflows/quality.yml",)
COMMON_MANUAL = ("docs/testing/manual-testing.md",)

EVIDENCE_BY_AREA: dict[str, tuple[str, ...]] = {
    "installation-initialization": (
        *COMMON_HOSTED,
        "docs/milestones/u12/exit-review.md",
    ),
    "no-cost-historical-acquisition": ("docs/milestones/u9/exit-review.md",),
    "local-csv-fallback": (
        *COMMON_MANUAL,
        "docs/milestones/u11/quickstart.md",
    ),
    "dataset-quality-revision-lineage": (
        "docs/milestones/u9/exit-review.md",
        "docs/milestones/u10/exit-review.md",
    ),
    "deterministic-analysis": COMMON_MANUAL,
    "backtesting-paper-evidence": COMMON_MANUAL,
    "ml-experiment-diagnostics": (
        *COMMON_MANUAL,
        "docs/milestones/u8/exit-review.md",
    ),
    "human-gated-validation": ("docs/milestones/u8/exit-review.md",),
    "workspace-browsing-export": ("docs/milestones/u10/exit-review.md",),
    "backup-restore": (
        *COMMON_HOSTED,
        "docs/milestones/u12/exit-review.md",
    ),
    "extension-boundaries": ("README.md", "docs/testing/manual-testing.md"),
    "offline-operation": ("docs/milestones/u11/quickstart.md",),
    "provider-outage-quota-policy": ("docs/milestones/u9/exit-review.md",),
    "corrupt-incomplete-artifacts": (
        "docs/milestones/u10/exit-review.md",
        "docs/milestones/u12/exit-review.md",
    ),
    "upgrade-rollback": (
        *COMMON_HOSTED,
        "docs/milestones/u12/exit-review.md",
    ),
    "documentation-cli-agreement": (
        "README.md",
        "docs/testing/manual-testing.md",
        "src/osca/cli.py",
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-version", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--defects", type=Path, default=Path("docs/milestones/u13/defects.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if set(EVIDENCE_BY_AREA) != set(ACCEPTANCE_AREAS):
        raise SystemExit("acceptance evidence map does not match the normative matrix")

    areas: list[dict[str, object]] = []
    missing: list[str] = []
    for area_id in ACCEPTANCE_AREAS:
        evidence = list(EVIDENCE_BY_AREA[area_id])
        absent = [path for path in evidence if not Path(path).is_file()]
        if absent:
            missing.extend(absent)
            status = "blocked"
            remediation = f"Restore required evidence authority: {', '.join(absent)}"
        else:
            status = "pass"
            remediation = None
        area: dict[str, object] = {
            "area_id": area_id,
            "status": status,
            "summary": f"{area_id} is covered by retained repository evidence.",
            "evidence": evidence,
        }
        if remediation is not None:
            area["remediation"] = remediation
        areas.append(area)

    defects = json.loads(args.defects.read_text(encoding="utf-8"))
    artifacts = list(args.artifact)
    if not artifacts:
        raise SystemExit("at least one release artifact is required")
    for artifact in artifacts:
        if not Path(artifact).is_file():
            missing.append(artifact)

    document = {
        "version": "1.0.0",
        "candidate_version": args.candidate_version,
        "source_commit": args.source_commit,
        "artifacts": artifacts,
        "areas": areas,
        "defects": defects,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if missing:
        raise SystemExit(f"missing acceptance evidence: {sorted(set(missing))}")


if __name__ == "__main__":
    main()
