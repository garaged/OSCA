"""Versioned desktop preference state owned by the Python application layer."""

from __future__ import annotations

import fcntl
import json
import os
import platform
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class DesktopProfileReference(BaseModel):
    """One user-selected OSCA profile reference retained by the desktop app."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(min_length=1, max_length=4096)
    label: str = Field(min_length=1, max_length=128)
    last_opened_at: str | None = None


class DesktopState(BaseModel):
    """Small profile-independent desktop state document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    family: Literal["osca.desktop-state"] = "osca.desktop-state"
    version: Literal["1.0.0"] = "1.0.0"
    profiles: tuple[DesktopProfileReference, ...] = ()
    selected_profile: str | None = Field(default=None, max_length=4096)


class DesktopStateStore:
    """Read and atomically replace versioned desktop preference state."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = (root or default_desktop_state_root()).expanduser().resolve()
        self._path = self._root / "desktop-state.json"
        self._lock_path = self._root / ".desktop-state.lock"

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> DesktopState:
        if not self._path.exists():
            return DesktopState()
        try:
            document = json.loads(self._path.read_text(encoding="utf-8"))
            return DesktopState.model_validate(document)
        except OSError as exc:
            raise ValueError(f"desktop state is unreadable at {self._path}: {exc}") from exc
        except (UnicodeDecodeError, json.JSONDecodeError, ValidationError) as exc:
            raise ValueError(f"desktop state is invalid at {self._path}: {exc}") from exc

    def remember(self, profile_root: Path, *, opened: bool) -> DesktopState:
        with self._exclusive_write_lock():
            state = self.load()
            canonical_path = str(profile_root.expanduser().resolve())
            current = next(
                (profile for profile in state.profiles if profile.path == canonical_path),
                None,
            )
            opened_at = (
                datetime.now(UTC).isoformat().replace("+00:00", "Z")
                if opened
                else current.last_opened_at
                if current is not None
                else None
            )
            replacement = DesktopProfileReference(
                path=canonical_path,
                label=_profile_label(profile_root),
                last_opened_at=opened_at,
            )
            profiles = tuple(
                replacement if profile.path == canonical_path else profile
                for profile in state.profiles
            )
            if current is None:
                profiles = (*profiles, replacement)
            updated = DesktopState(
                profiles=profiles,
                selected_profile=canonical_path,
            )
            self._write(updated)
            return updated

    def _write(self, state: DesktopState) -> None:
        self._root.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self._root,
                prefix=".desktop-state-",
                suffix=".tmp",
                delete=False,
            ) as stream:
                stream.write(state.model_dump_json(indent=2) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
                temporary_path = Path(stream.name)
            temporary_path.replace(self._path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    @contextmanager
    def _exclusive_write_lock(self) -> Iterator[None]:
        self._root.mkdir(parents=True, exist_ok=True)
        with self._lock_path.open("a+", encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def default_desktop_state_root() -> Path:
    """Return the supported-platform desktop state root without creating it."""

    override = os.environ.get("OSCA_DESKTOP_STATE_ROOT")
    if override:
        return Path(override)

    home = Path.home()
    if platform.system() == "Darwin":
        return home / "Library" / "Application Support" / "OSCA"
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home) / "osca"
    return home / ".config" / "osca"


def _profile_label(profile_root: Path) -> str:
    name = profile_root.expanduser().resolve().name.strip()
    return name or "OSCA Profile"
