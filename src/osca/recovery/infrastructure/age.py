from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from osca.recovery.infrastructure.package import RecoveryPackageError

_RECIPIENT = re.compile(r"^age1[023456789acdefghjklmnpqrstuvwxyz]{20,}$")


class AgeProcessContainer:
    container_id = "age/v1+x25519"

    def __init__(self, executable: Path, timeout_seconds: float = 30.0) -> None:
        if not executable.is_absolute():
            raise ValueError("age executable path must be absolute")
        self._executable = executable
        self._timeout_seconds = timeout_seconds

    def probe(self) -> None:
        self._run(("--version",), "recovery.encryption.unavailable")

    def encrypt(self, cleartext: Path, destination: Path, recipient: str) -> None:
        if not _RECIPIENT.fullmatch(recipient):
            raise RecoveryPackageError("recovery.recipient.invalid")
        destination.unlink(missing_ok=True)
        try:
            self._run(
                (
                    "--encrypt",
                    "--recipient",
                    recipient,
                    "--output",
                    str(destination),
                    str(cleartext),
                ),
                "recovery.encryption.failed",
            )
        except RecoveryPackageError:
            destination.unlink(missing_ok=True)
            raise

    def decrypt(self, package: Path, cleartext: Path, identity: bytes) -> None:
        if not identity or len(identity) > 64 * 1024:
            raise RecoveryPackageError("recovery.identity.invalid")
        cleartext.unlink(missing_ok=True)
        with TemporaryDirectory(prefix=".osca-age-identity-") as temporary:
            identity_path = Path(temporary) / "identity.txt"
            identity_path.write_bytes(identity)
            os.chmod(identity_path, 0o600)
            try:
                self._run(
                    (
                        "--decrypt",
                        "--identity",
                        str(identity_path),
                        "--output",
                        str(cleartext),
                        str(package),
                    ),
                    "recovery.decryption.failed",
                )
            except RecoveryPackageError:
                cleartext.unlink(missing_ok=True)
                raise

    def _run(self, arguments: tuple[str, ...], error_code: str) -> None:
        try:
            result = subprocess.run(
                (str(self._executable), *arguments),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                timeout=self._timeout_seconds,
                check=False,
                env={"PATH": os.defpath},
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise RecoveryPackageError(error_code) from error
        if result.returncode != 0:
            raise RecoveryPackageError(error_code)
