"""Bounded inter-process mutation locks for supported desktop profiles."""

from __future__ import annotations

import fcntl
import hashlib
import tempfile
from pathlib import Path
from types import TracebackType
from typing import Literal, Self, TextIO


class ProfileLockedError(ValueError):
    """Raised when another process currently owns the profile mutation lock."""


class ProfileMutationLock:
    """Hold a non-blocking exclusive lock for one bounded profile mutation."""

    def __init__(self, profile_root: Path) -> None:
        root = profile_root.expanduser().resolve()
        identity = hashlib.sha256(str(root).encode("utf-8")).hexdigest()
        self._lock_path = Path(tempfile.gettempdir()) / "osca-desktop-locks" / f"{identity}.lock"
        self._stream: TextIO | None = None

    @property
    def path(self) -> Path:
        return self._lock_path

    def __enter__(self) -> Self:
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        stream = self._lock_path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            stream.close()
            raise ProfileLockedError("profile is currently in use by another OSCA process") from exc
        except OSError:
            stream.close()
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
        return False


def profile_lock_status(profile_root: Path) -> Literal["available", "locked", "unavailable"]:
    """Probe whether a profile mutation lock can currently be acquired."""

    try:
        with ProfileMutationLock(profile_root):
            return "available"
    except ProfileLockedError:
        return "locked"
    except (OSError, ValueError):
        return "unavailable"
