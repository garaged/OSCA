import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from pydantic import ValidationError

from osca.provider_adapters import ProviderAdapterEndpoint
from osca.provider_preview.contracts import FredPreviewRequest, SecPreviewRequest
from osca.provider_preview.services import (
    ProviderPreviewError,
    SecPreviewService,
    evaluate_fred_preview,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m osca.provider_preview",
        description="Run safe P9 provider preview workflows.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command in ("sec-company-facts", "sec-submissions"):
        sec_parser = subparsers.add_parser(command)
        sec_parser.add_argument("cik")
        sec_parser.add_argument("--storage-root", type=Path, default=Path(".osca"))
        sec_parser.add_argument("--fixture-file", type=Path)
        sec_parser.add_argument("--enable-network", action="store_true")
        sec_parser.add_argument("--user-agent")
        sec_parser.add_argument("--force-refresh", action="store_true")

    fred_parser = subparsers.add_parser("fred-series")
    fred_parser.add_argument("series_id")
    fred_parser.add_argument("--enable-network", action="store_true")
    fred_parser.add_argument("--secret-reference")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command = cast(str, args.command)
    try:
        if command == "sec-company-facts":
            sec_request = SecPreviewRequest(
                endpoint=ProviderAdapterEndpoint.SEC_COMPANY_FACTS,
                cik=cast(str, args.cik),
                network_access_enabled=cast(bool, args.enable_network),
                fixture_path=cast(Path | None, args.fixture_file),
                user_agent=cast(str | None, args.user_agent),
                force_refresh=cast(bool, args.force_refresh),
            )
            return _run_sec_preview(
                sec_request,
                storage_root=cast(Path, args.storage_root),
            )

        if command == "sec-submissions":
            sec_request = SecPreviewRequest(
                endpoint=ProviderAdapterEndpoint.SEC_SUBMISSIONS,
                cik=cast(str, args.cik),
                network_access_enabled=cast(bool, args.enable_network),
                fixture_path=cast(Path | None, args.fixture_file),
                user_agent=cast(str | None, args.user_agent),
                force_refresh=cast(bool, args.force_refresh),
            )
            return _run_sec_preview(
                sec_request,
                storage_root=cast(Path, args.storage_root),
            )

        fred_request = FredPreviewRequest(
            series_id=cast(str, args.series_id),
            network_access_enabled=cast(bool, args.enable_network),
            secret_reference=cast(str | None, args.secret_reference),
        )
        evidence = evaluate_fred_preview(fred_request)
        print(json.dumps(evidence.model_dump(mode="json"), indent=2, sort_keys=True))
        return 2
    except (ProviderPreviewError, ValidationError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 2


def _run_sec_preview(
    request: SecPreviewRequest,
    *,
    storage_root: Path,
) -> int:
    evidence = SecPreviewService().run(request, storage_root=storage_root)
    print(json.dumps(evidence.model_dump(mode="json"), indent=2, sort_keys=True))
    return 0
