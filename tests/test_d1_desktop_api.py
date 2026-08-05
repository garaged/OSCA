from io import StringIO
from pathlib import Path

from osca.desktop_api.contracts import DesktopRequest
from osca.desktop_api.service import DesktopApplicationService
from osca.desktop_api.stdio import serve


def test_health_reports_safe_desktop_boundary() -> None:
    response = DesktopApplicationService().handle(
        DesktopRequest(request_id="health-1", method="system.health")
    )

    assert response.status == "ok"
    assert response.result is not None
    assert response.result["protocol_version"] == "1.0"
    assert response.result["live_order_execution"] is False


def test_unknown_method_fails_closed() -> None:
    response = DesktopApplicationService().handle(
        DesktopRequest(request_id="unknown-1", method="orders.submit")
    )

    assert response.status == "error"
    assert response.error is not None
    assert response.error.code == "method_not_found"


def test_profile_inspection_uses_explicit_storage_root(tmp_path: Path) -> None:
    response = DesktopApplicationService(storage_root=tmp_path).handle(
        DesktopRequest(request_id="profile-1", method="profile.inspect")
    )

    assert response.status == "ok"
    assert response.result == {
        "configured": True,
        "storage_root": str(tmp_path),
        "exists": True,
        "writable": True,
    }


def test_stdio_protocol_returns_one_response_per_request() -> None:
    stdin = StringIO(
        '{"protocol_version":"1.0","request_id":"health-2",'
        '"method":"system.health","params":{}}\n'
    )
    stdout = StringIO()

    assert serve(stdin, stdout) == 0
    output = stdout.getvalue()
    assert '"request_id":"health-2"' in output
    assert '"status":"ok"' in output


def test_stdio_protocol_rejects_invalid_json() -> None:
    stdout = StringIO()

    assert serve(StringIO("not-json\n"), stdout) == 0
    assert '"code":"invalid_request"' in stdout.getvalue()
