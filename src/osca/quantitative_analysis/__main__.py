from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from osca.quantitative_analysis import QuantitativeAnalysisRequest, analyze_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description="Run governed quantitative analysis.")
    parser.add_argument("payload_path", type=Path)
    parser.add_argument("dataset_revision_id", type=UUID)
    parser.add_argument("symbol")
    parser.add_argument("timeframe")
    parser.add_argument("--start", type=datetime.fromisoformat)
    parser.add_argument("--end", type=datetime.fromisoformat)
    parser.add_argument("--periods-per-year", type=int, default=252)
    parser.add_argument("--risk-free-rate", type=float, default=0.0)
    parser.add_argument("--confidence-level", type=float, default=0.95)
    parser.add_argument("--rsi-window", type=int, default=14)
    parser.add_argument("--atr-window", type=int, default=14)
    parser.add_argument("--bollinger-window", type=int, default=20)
    parser.add_argument("--fast-window", type=int, default=12)
    parser.add_argument("--slow-window", type=int, default=26)
    parser.add_argument("--signal-window", type=int, default=9)
    args = parser.parse_args()
    result = analyze_dataset(
        QuantitativeAnalysisRequest(
            dataset_revision_id=args.dataset_revision_id,
            payload_path=args.payload_path,
            symbol=args.symbol,
            timeframe=args.timeframe,
            start=args.start,
            end=args.end,
            periods_per_year=args.periods_per_year,
            risk_free_rate=args.risk_free_rate,
            confidence_level=args.confidence_level,
            rsi_window=args.rsi_window,
            atr_window=args.atr_window,
            bollinger_window=args.bollinger_window,
            fast_window=args.fast_window,
            slow_window=args.slow_window,
            signal_window=args.signal_window,
        )
    )
    print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
