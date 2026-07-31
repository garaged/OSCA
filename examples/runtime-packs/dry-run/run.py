#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys


def main() -> None:
    payload = json.load(sys.stdin)
    result = {
        "ok": True,
        "pack": "osca-dry-run",
        "input": payload,
        "network": os.environ.get("OSCA_EXTENSION_NETWORK"),
        "secrets": os.environ.get("OSCA_EXTENSION_SECRETS"),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
