from __future__ import annotations

import argparse
import json
from pathlib import Path

from osca.production_ingestion.contracts import (
    ProductionIngestionRequest,
    ProductionProvider,
)
from osca.production_ingestion.policy import provider_admission_policy
from osca.production_ingestion.services import run_production_ingestion


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OSCA governed production ingestion")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("policy", help="Show provider admission decisions")

    sec = subparsers.add_parser("sec-company-facts")
    sec.add_argument("--cik", required=True)
    sec.add_argument("--user-agent", required=True)
    sec.add_argument("--storage-root", type=Path, required=True)
    sec.add_argument("--enable-network", action="store_true")

    kraken = subparsers.add_parser("kraken-ohlc")
    kraken.add_argument("--pair", required=True)
    kraken.add_argument("--interval", type=int, default=1440)
    kraken.add_argument("--storage-root", type=Path, required=True)
    kraken.add_argument("--enable-network", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "policy":
        print(
            json.dumps(
                [decision.model_dump(mode="json") for decision in provider_admission_policy()],
                indent=2,
            )
        )
        return 0

    if args.command == "sec-company-facts":
        cik = str(args.cik).zfill(10)
        request = ProductionIngestionRequest(
            provider_id=ProductionProvider.SEC_EDGAR,
            resource_id="company_facts",
            endpoint_url=f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
            storage_root=str(args.storage_root),
            network_access_enabled=bool(args.enable_network),
            user_agent=str(args.user_agent),
        )
    else:
        request = ProductionIngestionRequest(
            provider_id=ProductionProvider.KRAKEN,
            resource_id="spot_ohlc",
            endpoint_url=(
                "https://api.kraken.com/0/public/OHLC"
                f"?pair={args.pair}&interval={args.interval}"
            ),
            storage_root=str(args.storage_root),
            network_access_enabled=bool(args.enable_network),
        )

    evidence = run_production_ingestion(request)
    print(evidence.model_dump_json(indent=2))
    return 0 if evidence.status.value == "succeeded" else 2


if __name__ == "__main__":
    raise SystemExit(main())
