import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import cast

from pydantic import ValidationError

from osca.runtime_routing.contracts import (
    RuntimeRoutingCapability,
    RuntimeRoutingRequest,
    RuntimeRoutingStatus,
)
from osca.runtime_routing.services import RuntimeRouter, routing_policy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m osca.runtime_routing",
        description="Inspect and run governed P10 capability routing.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("policy")

    local_parser = subparsers.add_parser("local-ohlcv")
    local_parser.add_argument("resource_id")
    local_parser.add_argument("payload_uri")
    local_parser.add_argument("--timeframe")
    local_parser.add_argument("--preferred-provider")
    local_parser.add_argument("--max-age-seconds", type=int)
    local_parser.add_argument("--allow-stale", action="store_true")

    for command in ("sec-company-facts", "sec-filings"):
        sec_parser = subparsers.add_parser(command)
        sec_parser.add_argument("resource_id")
        sec_parser.add_argument("--storage-root", type=Path, default=Path(".osca"))
        sec_parser.add_argument("--fixture-file", type=Path)
        sec_parser.add_argument("--enable-network", action="store_true")
        sec_parser.add_argument("--user-agent")
        sec_parser.add_argument("--force-refresh", action="store_true")
        sec_parser.add_argument("--preferred-provider")
        sec_parser.add_argument("--max-age-seconds", type=int)
        sec_parser.add_argument("--allow-stale", action="store_true")

    macro_parser = subparsers.add_parser("macro-series")
    macro_parser.add_argument("resource_id")
    macro_parser.add_argument("--preferred-provider")
    macro_parser.add_argument("--enable-network", action="store_true")
    macro_parser.add_argument("--secret-reference")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    command = cast(str, args.command)
    if command == "policy":
        print(json.dumps(routing_policy(), indent=2, sort_keys=True))
        return 0
    try:
        request, storage_root = _request_from_args(command, args)
        decision = RuntimeRouter().route(request, storage_root=storage_root)
        print(json.dumps(decision.model_dump(mode="json"), indent=2, sort_keys=True))
        return 0 if decision.status is RuntimeRoutingStatus.SELECTED else 2
    except (ValidationError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 2


def _request_from_args(
    command: str,
    args: argparse.Namespace,
) -> tuple[RuntimeRoutingRequest, Path]:
    if command == "local-ohlcv":
        return (
            RuntimeRoutingRequest(
                capability=RuntimeRoutingCapability.OHLCV,
                resource_id=cast(str, args.resource_id),
                local_payload_uri=cast(str, args.payload_uri),
                timeframe=cast(str | None, args.timeframe),
                preferred_provider=cast(str | None, args.preferred_provider),
                max_age_seconds=cast(int | None, args.max_age_seconds),
                allow_stale=cast(bool, args.allow_stale),
            ),
            Path(".osca"),
        )
    if command in {"sec-company-facts", "sec-filings"}:
        capability = (
            RuntimeRoutingCapability.COMPANY_FACTS
            if command == "sec-company-facts"
            else RuntimeRoutingCapability.FILINGS
        )
        return (
            RuntimeRoutingRequest(
                capability=capability,
                resource_id=cast(str, args.resource_id),
                preferred_provider=cast(str | None, args.preferred_provider),
                fixture_path=cast(Path | None, args.fixture_file),
                network_access_enabled=cast(bool, args.enable_network),
                user_agent=cast(str | None, args.user_agent),
                force_refresh=cast(bool, args.force_refresh),
                max_age_seconds=cast(int | None, args.max_age_seconds),
                allow_stale=cast(bool, args.allow_stale),
            ),
            cast(Path, args.storage_root),
        )
    return (
        RuntimeRoutingRequest(
            capability=RuntimeRoutingCapability.MACRO_SERIES,
            resource_id=cast(str, args.resource_id),
            preferred_provider=cast(str | None, args.preferred_provider),
            network_access_enabled=cast(bool, args.enable_network),
            secret_reference=cast(str | None, args.secret_reference),
        ),
        Path(".osca"),
    )
