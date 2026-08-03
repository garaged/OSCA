from __future__ import annotations

import argparse
import json
from pathlib import Path

from osca.release_acceptance import ACCEPTANCE_AREAS

EVIDENCE_BY_AREA: dict[str, tuple[str, ...]] = {
    "installation-initialization": (
        "tests/test_u11_operator_experience.py",
        "tests/test_u12_package_lifecycle.py",
        ".github/workflows/quality.yml",
    ),
    "no-cost-historical-acquisition": (
        "tests/test_u9_historical_acquisition.py",
        "docs/milestones/u9/exit-review.md",
    ),
    "local-csv-fallback": (
        "tests/test_u11_operator_experience.py",
        "docs/testing/manual-testing.md",
    ),
    "dataset-quality-revision-lineage": (
        "tests/test_u9_historical_acquisition.py",
        "tests/test_u10_research_evidence_workspace.py",
    ),
    "deterministic-analysis": (
        "tests/test_quantitative_analysis.py",
        "docs/testing/manual-testing.md",
    ),
    "backtesting-paper-evidence": (
        "tests/test_backtesting.py",
        "docs/testing/manual-testing.md",
    ),
    "ml-experiment-diagnostics": (
        "tests/test_ml_experiments.py",
        "tests/test_prediction_lab.py",
    ),
    "human-gated-validation": (
        "tests/test_model_validation.py",
        "docs/milestones/u8/exit-review.md",
    ),
    "workspace-browsing-export": (
        "tests/test_u10_research_evidence_workspace.py",
        "docs/milestones/u10/exit-review.md",
    ),
    "backup-restore": (
        "tests/test_u12_package_lifecycle.py",
        "docs/milestones/u12/exit-review.md",
    ),
    "extension-boundaries": (
        "tests/test_extension_runtime.py",
        "docs/testing/manual-testing.md",
    ),
    "offline-operation": (
        "tests/test_u11_operator_experience.py",
        "docs/milestones/u11/quickstart.md",
    ),
    "provider-outage-quota-policy": (
        "tests/test_u9_historical_acquisition.py",
        "docs/milestones/u9/exit-review.md",
    ),
    "corrupt-incomplete-artifacts": (
        "tests/test_u10_research_evidence_workspace.py",
        "tests/test_u12_package_lifecycle.py",
    ),
    "upgrade-rollback": (
        "tests/test_u12_package_lifecycle.py",
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
