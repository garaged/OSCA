from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.state import DesktopStateStore


def test_desktop_state_keeps_selected_profile_process_local(tmp_path: Path) -> None:
    state_root = tmp_path / "state"
    profile_a = tmp_path / "profile-a"
    profile_b = tmp_path / "profile-b"
    profile_a.mkdir()
    profile_b.mkdir()

    first = DesktopStateStore(state_root)
    second = DesktopStateStore(state_root)

    first.remember(profile_a, opened=True)
    second.remember(profile_b, opened=True)

    assert first.load().selected_profile == str(profile_a.resolve())
    assert second.load().selected_profile == str(profile_b.resolve())
    assert DesktopStateStore(state_root).load().selected_profile == str(profile_b.resolve())


def test_open_profile_lease_is_reentrant_for_owner_and_locked_for_other_process(tmp_path: Path) -> None:
    state_root = tmp_path / "state"
    profile = tmp_path / "profile"
    profile.mkdir()

    store = DesktopStateStore(state_root)
    store.remember(profile, opened=True)

    with ProfileMutationLock(profile):
        pass

    script = (
        "from pathlib import Path; "
        "from osca.desktop_api.profile_lock import profile_lock_status; "
        f"print(profile_lock_status(Path({str(profile)!r})))"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "locked"


def test_selecting_without_open_releases_process_profile_lease(tmp_path: Path) -> None:
    state_root = tmp_path / "state"
    profile_a = tmp_path / "profile-a"
    profile_b = tmp_path / "profile-b"
    profile_a.mkdir()
    profile_b.mkdir()

    store = DesktopStateStore(state_root)
    store.remember(profile_a, opened=True)
    store.remember(profile_b, opened=False)

    script = (
        "from pathlib import Path; "
        "from osca.desktop_api.profile_lock import profile_lock_status; "
        f"print(profile_lock_status(Path({str(profile_a)!r})))"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "available"
    assert store.load().selected_profile == str(profile_b.resolve())
