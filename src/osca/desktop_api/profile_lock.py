"""Bounded inter-process locks for supported desktop profiles."""

from __future__ import annotations

import fcntl
import hashlib
import os
import tempfile
from pathlib import Path
from types import TracebackType
from typing import Literal, Self, TextIO

_BROKER_OWNED_PROFILE_ENV = "OSCA_DESKTOP_OWNED_PROFILE"
_FNV_OFFSET_BASIS = 0xCBF29CE484222325
_FNV_PRIME = 0x100000001B3
_U64_MASK = 0xFFFFFFFFFFFFFFFF


class ProfileLockedError(ValueError):
    """Raised when another process or desktop session owns the profile."""


def _stable_profile_identity(profile_root: Path) -> int:
    value = _FNV_OFFSET_BASIS
    for byte in str(profile_root.expanduser().resolve()).encode("utf-8"):
        value = ((value ^ byte) * _FNV_PRIME) & _U64_MASK
    return value


def profile_session_lock_path(profile_root: Path) -> Path:
    """Return the broker/CLI shared session-lock path for a profile."""

    identity = _stable_profile_identity(profile_root)
    return Path(tempfile.gettempdir()) / "osca-desktop-session-locks" / f"{identity:016x}.lock"


def _broker_owns_profile(profile_root: Path) -> bool:
    owned = os.environ.get(_BROKER_OWNED_PROFILE_ENV)
    if not owned:
        return False
    return Path(owned).expanduser().resolve() == profile_root.expanduser().resolve()


class ProfileMutationLock:
    """Hold session compatibility plus one bounded mutation lock.

    Standalone Python/CLI mutations hold the shared desktop session lease for the
    full mutation so they cannot bypass an open desktop window. Broker-launched
    sidecars are explicitly authorized for the broker-owned profile and therefore
    reuse the broker's lifetime lease while still taking the normal mutation lock.
    """

    def __init__(self, profile_root: Path) -> None:
        root = profile_root.expanduser().resolve()
        identity = hashlib.sha256(str(root).encode("utf-8")).hexdigest()
        self._profile_root = root
        self._session_lock_path = profile_session_lock_path(root)
        self._lock_path = Path(tempfile.gettempdir()) / "osca-desktop-locks" / f"{identity}.lock"
        self._session_stream: TextIO | None = None
        self._stream: TextIO | None = None

    @property
    def path(self) -> Path:
        return self._lock_path

    @property
    def session_path(self) -> Path:
        return self._session_lock_path

    def __enter__(self) -> Self:
        if not _broker_owns_profile(self._profile_root):
            self._session_lock_path.parent.mkdir(parents=True, exist_ok=True)
            session_stream = self._session_lock_path.open("a+", encoding="utf-8")
            try:
                fcntl.flock(session_stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                session_stream.close()
                raise ProfileLockedError(
                    "profile is already open in another OSCA window or process"
                ) from exc
            except OSError:
                session_stream.close()
                raise
            self._session_stream = session_stream

        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        stream = self._lock_path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            stream.close()
            self._release_session_lock()
            raise ProfileLockedError("profile is currently in use by another OSCA process") from exc
        except OSError:
            stream.close()
            self._release_session_lock()
            raise
        self._stream = stream
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        stream = self._stream
        self._stream = None
        if stream is not None:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            stream.close()
        self._release_session_lock()
        return False

    def _release_session_lock(self) -> None:
        stream = self._session_stream
        self._session_stream = None
        if stream is not None:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            stream.close()


def profile_lock_status(profile_root: Path) -> Literal["available", "locked", "unavailable"]:
    """Probe whether a profile can be safely mutated by this process."""

    try:
        with ProfileMutationLock(profile_root):
            return "available"
    except ProfileLockedError:
        return "locked"
    except (OSError, ValueError):
        return "unavailable"
