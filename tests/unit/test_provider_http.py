from collections.abc import Mapping
from io import BytesIO
from urllib.request import Request

import pytest

from osca.provider.infrastructure import BoundedJsonTransport
from osca.provider.infrastructure.http import Response


class FakeResponse:
    headers: Mapping[str, str]

    def __init__(self, payload: bytes, *, encoding: str = "identity") -> None:
        self._stream = BytesIO(payload)
        self.headers = {"Content-Encoding": encoding}

    def __enter__(self) -> Response:
        return self

    def __exit__(self, *args: object) -> None:
        self._stream.close()

    def read(self, amount: int = -1) -> bytes:
        return self._stream.read(amount)


def test_transport_enforces_endpoint_query_and_response_bounds() -> None:
    seen: list[str] = []

    def open_request(request: Request, timeout: float) -> Response:
        seen.append(request.full_url)
        assert timeout == 2.0
        return FakeResponse(b'{"values": []}')

    transport = BoundedJsonTransport(
        base_url="https://api.example.test/v1/",
        allowed_host="api.example.test",
        allowed_query_keys=frozenset({"symbol"}),
        timeout_seconds=2.0,
        maximum_response_bytes=32,
        open_request=open_request,
    )
    assert transport.get("daily", {"symbol": "ACME"}) == {"values": []}
    assert seen == ["https://api.example.test/v1/daily?symbol=ACME"]
    with pytest.raises(ValueError, match="unapproved"):
        transport.get("daily", {"api_key": "must-not-enter-a-url"})
    with pytest.raises(ValueError, match="safe relative"):
        transport.get("https://attacker.test/data", {})


def test_transport_rejects_oversize_compression_and_non_object_json() -> None:
    responses = iter(
        (
            FakeResponse(b"x" * 17),
            FakeResponse(b"{}", encoding="gzip"),
            FakeResponse(b"[]"),
        )
    )
    transport = BoundedJsonTransport(
        base_url="https://api.example.test/",
        allowed_host="api.example.test",
        allowed_query_keys=frozenset(),
        maximum_response_bytes=16,
        open_request=lambda _request, _timeout: next(responses),
    )
    with pytest.raises(ValueError, match="byte bound"):
        transport.get("daily", {})
    with pytest.raises(ValueError, match="compressed"):
        transport.get("daily", {})
    with pytest.raises(ValueError, match="root"):
        transport.get("daily", {})
