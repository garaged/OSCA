from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

from osca.runtime_extensions import (
    RuntimeExtensionStatus,
    RuntimePackRequest,
    execute_runtime_pack,
    validate_runtime_pack,
)


def test_committed_dry_run_pack_exercises_safe_runtime(tmp_path: Path) -> None:
    source = Path("examples/runtime-packs/dry-run")
    pack = tmp_path / "dry-run"
    shutil.copytree(source, pack)

    subprocess.run(
        [sys.executable, str(pack / "prepare.py")],
        check=True,
        capture_output=True,
        text=True,
    )

    request = RuntimePackRequest(
        pack_directory=str(pack),
        storage_root=str(tmp_path / "storage"),
        input_payload='{"symbol":"AAPL"}',
    )
    validation = validate_runtime_pack(request)
    assert validation.status is RuntimeExtensionStatus.VALIDATED

    blocked = execute_runtime_pack(request)
    assert blocked.status is RuntimeExtensionStatus.POLICY_BLOCKED
    assert "execution-disabled" in blocked.findings

    executed = execute_runtime_pack(request.model_copy(update={"enable_execution": True}))
    assert executed.status is RuntimeExtensionStatus.SUCCEEDED
    assert executed.stdout_uri is not None
    output = json.loads(Path(executed.stdout_uri).read_text())
    assert output == {
        "input": {"symbol": "AAPL"},
        "network": "disabled",
        "ok": True,
        "pack": "osca-dry-run",
        "secrets": "disabled",
    }
