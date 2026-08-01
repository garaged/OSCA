from __future__ import annotations

import argparse
import json
from pathlib import Path

from osca.model_validation import ModelValidationRequest, validate_model_research


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate promoted model evidence through local research backtesting."
    )
    parser.add_argument("request_json", type=Path)
    args = parser.parse_args()
    request = ModelValidationRequest.model_validate_json(args.request_json.read_text())
    result = validate_model_research(request)
    print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
