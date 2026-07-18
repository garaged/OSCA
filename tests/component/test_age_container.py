import os
from pathlib import Path

import pytest

from osca.recovery.infrastructure.age import AgeProcessContainer
from osca.recovery.infrastructure.package import RecoveryPackageError

_RECIPIENT = "age1" + "q" * 58


def _fake_age(tmp_path: Path) -> Path:
    executable = tmp_path / "age"
    executable.write_text(
        """#!/bin/sh
set -eu
if [ "$1" = "--version" ]; then
  echo "1.2.1"
  exit 0
fi
mode="$1"
shift
input=""
output=""
identity=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --recipient) shift 2 ;;
    --identity) identity="$2"; shift 2 ;;
    --output) output="$2"; shift 2 ;;
    *) input="$1"; shift ;;
  esac
done
if [ "$mode" = "--decrypt" ]; then
  [ "$(cat "$identity")" = "AGE-SECRET-KEY-TEST" ] || exit 2
fi
cp "$input" "$output"
"""
    )
    executable.chmod(0o700)
    return executable


def test_age_adapter_round_trip_and_identity_cleanup(tmp_path: Path) -> None:
    adapter = AgeProcessContainer(_fake_age(tmp_path))
    adapter.probe()
    cleartext = tmp_path / "cleartext"
    encrypted = tmp_path / "backup.age"
    restored = tmp_path / "restored"
    cleartext.write_bytes(b"protected")
    adapter.encrypt(cleartext, encrypted, _RECIPIENT)
    adapter.decrypt(encrypted, restored, b"AGE-SECRET-KEY-TEST")
    assert restored.read_bytes() == b"protected"
    assert not any(path.name.startswith(".osca-age-identity-") for path in Path("/tmp").iterdir())


def test_invalid_recipient_fails_before_process(tmp_path: Path) -> None:
    adapter = AgeProcessContainer(_fake_age(tmp_path))
    with pytest.raises(RecoveryPackageError, match=r"recipient\.invalid"):
        adapter.encrypt(tmp_path / "missing", tmp_path / "output", "not-an-age-recipient")


def test_wrong_identity_leaves_no_cleartext(tmp_path: Path) -> None:
    adapter = AgeProcessContainer(_fake_age(tmp_path))
    package = tmp_path / "backup.age"
    output = tmp_path / "cleartext"
    package.write_bytes(b"ciphertext fixture")
    with pytest.raises(RecoveryPackageError, match=r"decryption\.failed"):
        adapter.decrypt(package, output, b"wrong")
    assert not output.exists()


def test_unavailable_executable_is_safely_classified(tmp_path: Path) -> None:
    adapter = AgeProcessContainer((tmp_path / "missing").resolve())
    with pytest.raises(RecoveryPackageError, match=r"encryption\.unavailable"):
        adapter.probe()


def test_executable_must_be_absolute() -> None:
    with pytest.raises(ValueError, match="absolute"):
        AgeProcessContainer(Path(os.curdir) / "age")
