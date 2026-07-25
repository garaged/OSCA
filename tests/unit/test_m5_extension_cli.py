import json
from pathlib import Path

from typer.testing import CliRunner

from osca.bootstrap.cli import app
from osca.extensions.api import (
    ExtensionCategory,
    ExtensionEntryPoint,
    ExtensionManifest,
    ExtensionPermission,
    ExtensionPermissionKind,
    ExtensionSchemaRef,
    ExtensionTrustTier,
)

DIGEST = "sha256:" + "d" * 64


def manifest_file(tmp_path: Path) -> Path:
    manifest = ExtensionManifest(
        package_id="cli-extension",
        name="CLI Extension",
        publisher="garaged",
        package_version="1.0.0",
        category=ExtensionCategory.VISUALIZATION,
        entry_points=(
            ExtensionEntryPoint(
                name="cli",
                contract_family="osca.visualization.specification",
                callable_ref="cli_extension:render",
            ),
        ),
        osca_compatibility=(">=0.1.0",),
        output_schemas=(
            ExtensionSchemaRef(
                name="cli_output",
                schema_family="osca.visualization.specification",
                version="1.0.0",
            ),
        ),
        permissions=(
            ExtensionPermission(
                kind=ExtensionPermissionKind.FILESYSTEM,
                scope="exports:write",
                rationale="Write requested exports",
            ),
        ),
        integrity_digest=DIGEST,
        license="Apache-2.0",
        provenance="local CLI fixture",
        trust_tier=ExtensionTrustTier.VERIFIED,
    )
    path = tmp_path / "extension-manifest.json"
    path.write_text(manifest.model_dump_json(), encoding="utf-8")
    return path


def test_extension_install_and_list_cli(tmp_path: Path) -> None:
    runner = CliRunner()
    database = tmp_path / "extensions.sqlite"
    manifest = manifest_file(tmp_path)

    install = runner.invoke(
        app,
        [
            "extension-install",
            str(manifest),
            "--source-uri",
            "file:///extensions/cli-extension.oscaext",
            "--database",
            str(database),
        ],
    )

    assert install.exit_code == 0
    installed = json.loads(install.stdout)
    assert installed["package_id"] == "cli-extension"

    listing = runner.invoke(app, ["extension-list", "--database", str(database)])

    assert listing.exit_code == 0
    records = json.loads(listing.stdout)
    assert [record["installation_id"] for record in records] == [
        installed["installation_id"]
    ]


def test_extension_activate_cli_records_decision(tmp_path: Path) -> None:
    runner = CliRunner()
    database = tmp_path / "extensions.sqlite"
    manifest = manifest_file(tmp_path)
    install = runner.invoke(
        app,
        [
            "extension-install",
            str(manifest),
            "--source-uri",
            "file:///extensions/cli-extension.oscaext",
            "--database",
            str(database),
        ],
    )
    installed = json.loads(install.stdout)

    activation = runner.invoke(
        app,
        [
            "extension-activate",
            str(manifest),
            installed["installation_id"],
            "--database",
            str(database),
        ],
    )

    assert activation.exit_code == 0
    decision = json.loads(activation.stdout)
    assert decision["installation_id"] == installed["installation_id"]
    assert decision["approved"] is True


def test_extension_activate_cli_rejects_unknown_installation(tmp_path: Path) -> None:
    runner = CliRunner()
    database = tmp_path / "extensions.sqlite"
    manifest = manifest_file(tmp_path)

    activation = runner.invoke(
        app,
        [
            "extension-activate",
            str(manifest),
            "00000000-0000-0000-0000-000000000000",
            "--database",
            str(database),
        ],
    )

    assert activation.exit_code != 0
    assert "installation not found" in activation.output
