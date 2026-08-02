from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _wheel_metadata(wheel: Path) -> tuple[str, list[str]]:
    with zipfile.ZipFile(wheel) as archive:
        metadata_name = next(
            name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
        )
        lines = archive.read(metadata_name).decode("utf-8").splitlines()
    version = next(line.removeprefix("Version: ") for line in lines if line.startswith("Version: "))
    dependencies = sorted(
        line.removeprefix("Requires-Dist: ") for line in lines if line.startswith("Requires-Dist: ")
    )
    return version, dependencies


def build_release_artifacts(
    dist_dir: Path,
    output_dir: Path,
    *,
    source_commit: str,
    source_repository: str,
) -> dict[str, Any]:
    wheels = sorted(dist_dir.glob("*.whl"))
    sdists = sorted(dist_dir.glob("*.tar.gz"))
    if len(wheels) != 1:
        raise ValueError("exactly one wheel is required")
    if len(sdists) != 1:
        raise ValueError("exactly one source distribution is required")

    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = wheels + sdists
    version, dependencies = _wheel_metadata(wheels[0])
    checksums = [
        {
            "path": artifact.name,
            "sha256": _sha256(artifact),
            "size": artifact.stat().st_size,
        }
        for artifact in artifacts
    ]
    checksum_path = output_dir / "SHA256SUMS"
    checksum_path.write_text(
        "".join(f"{item['sha256']}  {item['path']}\n" for item in checksums),
        encoding="utf-8",
    )

    sbom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:osca-{version}-{source_commit[:12]}",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": "osca",
                "version": version,
                "purl": f"pkg:pypi/osca@{version}",
            }
        },
        "components": [
            {
                "type": "library",
                "name": dependency.split(" ", 1)[0],
                "version": dependency,
            }
            for dependency in dependencies
        ],
    }
    sbom_path = output_dir / "osca-sbom.cdx.json"
    sbom_path.write_text(json.dumps(sbom, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    provenance = {
        "family": "osca.release-provenance",
        "version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "osca_version": version,
        "source_commit": source_commit,
        "source_repository": source_repository,
        "artifacts": checksums,
        "checksum_manifest": {
            "path": checksum_path.name,
            "sha256": _sha256(checksum_path),
        },
        "sbom": {"path": sbom_path.name, "sha256": _sha256(sbom_path)},
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_orders_enabled": False,
    }
    provenance_path = output_dir / "osca-provenance.json"
    provenance_path.write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-repository", required=True)
    args = parser.parse_args()
    result = build_release_artifacts(
        args.dist_dir,
        args.output_dir,
        source_commit=args.source_commit,
        source_repository=args.source_repository,
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
