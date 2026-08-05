"""Versioned desktop application API for the OSCA desktop host."""

from osca.desktop_api.contracts import DesktopRequest, DesktopResponse
from osca.desktop_api.service import DesktopApplicationService

__all__ = ["DesktopApplicationService", "DesktopRequest", "DesktopResponse"]
