"""Line-delimited JSON entrypoint for the supervised desktop sidecar."""

import json
import os
import sys
from pathlib import Path
from typing import TextIO

from pydantic import ValidationError

from osca.desktop_api.contracts import DesktopError, DesktopRequest, DesktopResponse
from osca.desktop_api.d3_acquisition_service import D3AcquisitionApplicationService

MAX_MESSAGE_BYTES = 1_048_576


def _error_response(request_id: str, code: str, message: str) -> DesktopResponse:
    return DesktopResponse(
        request_id=request_id,
        status="error",
        error=DesktopError(code=code, message=message),
    )


def serve(stdin: TextIO, stdout: TextIO) -> int:
    storage_value = os.environ.get("OSCA_STORAGE_ROOT")
    service = D3AcquisitionApplicationService(
        storage_root=Path(storage_value).expanduser() if storage_value else None
    )
    for raw_line in stdin:
        if len(raw_line.encode("utf-8")) > MAX_MESSAGE_BYTES:
            response = _error_response("unknown", "message_too_large", "Request exceeds 1 MiB")
        else:
            try:
                payload = json.loads(raw_line)
                request = DesktopRequest.model_validate(payload)
                response = service.handle(request)
            except (json.JSONDecodeError, ValidationError) as exc:
                response = _error_response("unknown", "invalid_request", str(exc))
        stdout.write(response.model_dump_json() + "\n")
        stdout.flush()
    return 0


def main() -> None:
    raise SystemExit(serve(sys.stdin, sys.stdout))


if __name__ == "__main__":
    main()
