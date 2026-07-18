import json
from collections.abc import Callable, Mapping
from typing import Any, Protocol
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class Response(Protocol):
    headers: Mapping[str, str]

    def read(self, amount: int = -1) -> bytes: ...
    def __enter__(self) -> "Response": ...
    def __exit__(self, *args: object) -> None: ...


OpenRequest = Callable[[Request, float], Response]


class _RejectRedirects(HTTPRedirectHandler):
    def redirect_request(
        self,
        request: Request,
        file_pointer: object,
        code: int,
        message: str,
        headers: object,
        new_url: str,
    ) -> None:
        raise ValueError("provider redirects are prohibited")


class BoundedJsonTransport:
    """HTTPS-only JSON transport with fixed host, no redirects, and bounded bytes/time."""

    def __init__(
        self,
        *,
        base_url: str,
        allowed_host: str,
        allowed_query_keys: frozenset[str],
        timeout_seconds: float = 10.0,
        maximum_response_bytes: int = 2_000_000,
        open_request: OpenRequest | None = None,
    ) -> None:
        parsed = urlsplit(base_url)
        if parsed.scheme != "https" or parsed.hostname != allowed_host or parsed.query:
            raise ValueError("base URL must be an exact allowed HTTPS origin")
        if timeout_seconds <= 0 or maximum_response_bytes <= 0:
            raise ValueError("transport bounds must be positive")
        self._base_url = base_url.rstrip("/") + "/"
        self._allowed_host = allowed_host
        self._allowed_query_keys = allowed_query_keys
        self._timeout_seconds = timeout_seconds
        self._maximum_response_bytes = maximum_response_bytes
        self._open_request = open_request or self._default_open

    def get(
        self,
        path: str,
        query: Mapping[str, str | int],
        *,
        headers: Mapping[str, str] | None = None,
    ) -> Mapping[str, Any]:
        relative = urlsplit(path)
        if relative.scheme or relative.netloc or path.startswith("/") or ".." in relative.path:
            raise ValueError("provider path must be a safe relative path")
        if not set(query).issubset(self._allowed_query_keys):
            raise ValueError("provider query contains an unapproved key")
        if any(len(str(value)) > 256 for value in query.values()):
            raise ValueError("provider query value exceeds its bound")
        url = urljoin(self._base_url, relative.path)
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.hostname != self._allowed_host:
            raise ValueError("resolved provider URL violates endpoint policy")
        encoded_url = f"{url}?{urlencode(query)}" if query else url
        request = Request(
            encoded_url,
            headers={"Accept": "application/json", **dict(headers or {})},
            method="GET",
        )
        with self._open_request(request, self._timeout_seconds) as response:
            encoding = response.headers.get("Content-Encoding", "identity").lower()
            if encoding not in {"", "identity"}:
                raise ValueError("compressed provider responses are prohibited")
            payload = response.read(self._maximum_response_bytes + 1)
        if len(payload) > self._maximum_response_bytes:
            raise ValueError("provider response exceeds its byte bound")
        decoded = json.loads(payload)
        if not isinstance(decoded, dict):
            raise ValueError("provider JSON root must be an object")
        return decoded

    @staticmethod
    def _default_open(request: Request, timeout: float) -> Response:
        opener = build_opener(_RejectRedirects())
        return opener.open(request, timeout=timeout)  # type: ignore[no-any-return]
