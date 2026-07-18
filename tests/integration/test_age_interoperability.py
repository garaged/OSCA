import os
import subprocess
from pathlib import Path

import pytest

from osca.recovery.infrastructure.age import AgeProcessContainer


def test_age_reference_cli_interoperability(tmp_path: Path) -> None:
    configured = os.environ.get("AGE_TEST_EXECUTABLE")
    if configured is None:
        pytest.skip("AGE_TEST_EXECUTABLE is required for interoperability evidence")
    executable = Path(configured).resolve()
    keygen = executable.with_name("age-keygen")
    identity = tmp_path / "identity.txt"
    subprocess.run(
        (str(keygen), "--output", str(identity)),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    recipient = subprocess.run(
        (str(keygen), "-y", str(identity)),
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    adapter = AgeProcessContainer(executable)
    adapter.probe()
    cleartext = tmp_path / "cleartext"
    cleartext.write_bytes(b"osca age interoperability")

    osca_package = tmp_path / "osca.age"
    raw_output = tmp_path / "raw-output"
    adapter.encrypt(cleartext, osca_package, recipient)
    subprocess.run(
        (
            str(executable),
            "--decrypt",
            "--identity",
            str(identity),
            "--output",
            str(raw_output),
            str(osca_package),
        ),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    assert raw_output.read_bytes() == cleartext.read_bytes()

    raw_package = tmp_path / "raw.age"
    osca_output = tmp_path / "osca-output"
    subprocess.run(
        (
            str(executable),
            "--encrypt",
            "--recipient",
            recipient,
            "--output",
            str(raw_package),
            str(cleartext),
        ),
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    adapter.decrypt(raw_package, osca_output, identity.read_bytes())
    assert osca_output.read_bytes() == cleartext.read_bytes()
