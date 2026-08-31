from __future__ import annotations

import json
from pathlib import Path

from scripts.prepare_desktop_acceptance import prepare


def test_prepare_creates_deterministic_d5_to_d10_acceptance_profile(tmp_path: Path) -> None:
    root = tmp_path / ".osca" / "desktop-acceptance"
    manifest = prepare(root, reset=True)

    assert manifest["network_access_enabled"] is False
    assert manifest["recommendations_enabled"] is False
    assert manifest["real_capital_execution_enabled"] is False
    assert manifest["sample_import"]["symbols"] == ["AAPL-SYNTHETIC", "MSFT-SYNTHETIC"]
    assert manifest["workbench"]["aligned_return_count"] > 0
    assert manifest["backtest"] == {"result_id": 1, "bars_processed": 220, "trade_count": 11}
    assert manifest["ml_experiment"]["status"] in {"completed", "review_required"}
    assert manifest["ml_experiment"]["output_digest"]
    assert manifest["ml_experiment"]["automatic_promotion_enabled"] is False
    retained = json.loads(
        (root / "evidence" / "acceptance-manifest.json").read_text(encoding="utf-8")
    )
    assert retained == manifest


def test_prepare_rejects_an_unsafe_reset_target(tmp_path: Path) -> None:
    try:
        prepare(tmp_path / "not-acceptance", reset=True)
    except ValueError as error:
        assert ".osca/.../desktop-acceptance" in str(error)
    else:
        raise AssertionError("unsafe acceptance root was accepted")
