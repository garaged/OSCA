"""Profile-scoped strategies and backtest evidence for D7 desktop."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast
from uuid import uuid4

import pyarrow.parquet as pq

from osca.desktop_api.service import DesktopServiceError
from osca.desktop_api.workbench_data import GovernedDataset, resolve_governed_dataset

_SCHEMA_VERSION = 2
_MAX_SENSITIVITY_RUNS = 12
_STRATEGY_STATUSES = {"active", "archived"}
_FORBIDDEN_KEYS = {
    "api_key",
    "broker",
    "code",
    "credential",
    "exec",
    "filesystem",
    "import",
    "notebook",
    "order",
    "password",
    "path",
    "provider",
    "python",
    "secret",
    "shell",
    "sql",
    "token",
}
_SUPPORTED_RULES = {"close_above_sma", "close_below_sma"}
_FUTURE_RULES = {"future_close_above", "future_close_below", "next_close_above"}


@dataclass(frozen=True)
class _Bar:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


def create_strategy(
    profile_root: Path,
    *,
    name: str,
    objective: str,
    asset_id: str,
    timeframe: str,
    dsl: dict[str, Any],
) -> dict[str, Any]:
    normalized_name = _bounded_text(name, "Strategy name", limit=80)
    normalized_objective = _bounded_text(objective, "Strategy objective", limit=1000)
    normalized_asset = _bounded_text(asset_id, "Strategy asset", limit=128)
    normalized_timeframe = _bounded_text(timeframe, "Strategy timeframe", limit=20)
    normalized_dsl = _safe_json_object(dsl, "Strategy DSL", limit=32_768)
    validation = validate_strategy_dsl(normalized_dsl)
    strategy_uuid = str(uuid4())
    version_uuid = str(uuid4())
    with _connect(profile_root) as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO strategies(strategy_uuid, name, objective, asset_id, timeframe) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    strategy_uuid,
                    normalized_name,
                    normalized_objective,
                    normalized_asset,
                    normalized_timeframe,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise DesktopServiceError(
                "strategy_conflict",
                "A strategy with that name already exists.",
            ) from exc
        assert cursor.lastrowid is not None
        strategy_id = int(cursor.lastrowid)
        version_id = _insert_version(
            connection,
            strategy_id=strategy_id,
            version_uuid=version_uuid,
            version_number=1,
            dsl=normalized_dsl,
            validation=validation,
            summary=_strategy_summary(normalized_dsl),
        )
        connection.execute(
            "UPDATE strategies SET current_version_id=? WHERE id=?",
            (version_id, strategy_id),
        )
        _append_event(
            connection,
            strategy_id,
            "strategy.created",
            {"strategy_uuid": strategy_uuid, "version_id": version_id},
        )
        return _single_strategy(connection, strategy_id)


def list_strategies(profile_root: Path, *, include_archived: bool = False) -> dict[str, Any]:
    statuses = ["active"]
    if include_archived:
        statuses.append("archived")
    placeholders = ",".join("?" for _ in statuses)
    with _connect(profile_root) as connection:
        rows = connection.execute(
            "SELECT * FROM strategies "
            f"WHERE status IN ({placeholders}) ORDER BY lower(name), id",
            tuple(statuses),
        ).fetchall()
        strategies = [_strategy_payload(connection, int(row["id"]), detail=False) for row in rows]
    return {
        "family": "osca.desktop-strategy-list.result",
        "version": "1.0.0",
        "schema_version": _SCHEMA_VERSION,
        "strategies": strategies,
    }


def get_strategy(profile_root: Path, strategy_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        _require_strategy(connection, strategy_id)
        return _single_strategy(connection, strategy_id)


def create_strategy_version(
    profile_root: Path,
    *,
    strategy_id: int,
    dsl: dict[str, Any],
    summary: str | None = None,
) -> dict[str, Any]:
    normalized_dsl = _safe_json_object(dsl, "Strategy DSL", limit=32_768)
    normalized_summary = (
        _bounded_text(summary, "Strategy version summary", limit=240)
        if summary is not None
        else _strategy_summary(normalized_dsl)
    )
    validation = validate_strategy_dsl(normalized_dsl)
    with _connect(profile_root) as connection:
        _require_mutable_strategy(connection, strategy_id)
        next_version = int(
            connection.execute(
                "SELECT COALESCE(MAX(version_number), 0) + 1 FROM strategy_versions "
                "WHERE strategy_id=?",
                (strategy_id,),
            ).fetchone()[0]
        )
        version_id = _insert_version(
            connection,
            strategy_id=strategy_id,
            version_uuid=str(uuid4()),
            version_number=next_version,
            dsl=normalized_dsl,
            validation=validation,
            summary=normalized_summary,
        )
        connection.execute(
            "UPDATE strategies SET current_version_id=?, "
            "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id=?",
            (version_id, strategy_id),
        )
        _append_event(
            connection,
            strategy_id,
            "strategy.version_created",
            {"version_id": version_id, "version_number": next_version},
        )
        return {
            "family": "osca.desktop-strategy-version.result",
            "version": "1.0.0",
            "strategy": _strategy_payload(connection, strategy_id),
            "strategy_version": _version_payload(connection, version_id),
        }


def validate_strategy_dsl(dsl: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    if dsl.get("family") != "osca.strategy.dsl":
        findings.append(_finding("dsl_family", "error", "Strategy DSL family is unsupported."))
    if dsl.get("version") != "1.0.0":
        findings.append(_finding("dsl_version", "error", "Strategy DSL version is unsupported."))
    _find_forbidden(dsl, findings)
    for section in ("entry", "exit", "filter"):
        if section == "filter" and section not in dsl:
            continue
        rule = dsl.get(section)
        if not isinstance(rule, dict):
            findings.append(_finding(f"{section}_missing", "error", f"{section} rule is required."))
            continue
        rule_type = rule.get("type")
        if rule_type in _FUTURE_RULES:
            findings.append(_finding("lookahead_rule", "error", "Rule references future data."))
            continue
        if rule_type not in _SUPPORTED_RULES:
            findings.append(
                _finding("unsupported_rule", "error", f"{section} rule is unsupported.")
            )
        window = rule.get("window")
        if not isinstance(window, int) or isinstance(window, bool) or window < 2 or window > 252:
            findings.append(
                _finding(
                    f"{section}_window",
                    "error",
                    f"{section} rule window must be an integer from 2 through 252.",
                )
            )
    sizing = dsl.get("sizing", {})
    if not isinstance(sizing, dict) or sizing.get("type") != "fixed_fraction":
        findings.append(
            _finding("sizing_type", "error", "Only fixed_fraction sizing is supported.")
        )
    else:
        fraction = sizing.get("fraction")
        if not isinstance(fraction, int | float) or isinstance(fraction, bool):
            findings.append(
                _finding("sizing_fraction", "error", "Sizing fraction must be numeric.")
            )
        elif fraction <= 0 or fraction > 1:
            findings.append(
                _finding(
                    "sizing_fraction",
                    "error",
                    "Sizing fraction must be > 0 and <= 1.",
                )
            )
    costs = dsl.get("costs", {})
    if costs is not None and not isinstance(costs, dict):
        findings.append(_finding("costs_type", "error", "Costs must be an object."))
    elif isinstance(costs, dict):
        for key in ("fees_bps", "slippage_bps"):
            value = costs.get(key, 0.0)
            if not isinstance(value, int | float) or isinstance(value, bool) or value < 0:
                findings.append(_finding(key, "error", f"{key} must be a non-negative number."))
    return {
        "family": "osca.desktop-strategy-validation.result",
        "version": "1.0.0",
        "can_execute": not any(finding["severity"] == "error" for finding in findings),
        "findings": findings,
        "point_in_time_required": True,
        "arbitrary_code_execution_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "real_capital_execution_enabled": False,
    }


def run_backtest(
    profile_root: Path,
    *,
    strategy_id: int,
    strategy_version_id: int,
    initial_cash: float = 10_000.0,
) -> dict[str, Any]:
    if initial_cash <= 0:
        raise DesktopServiceError("invalid_parameters", "initial_cash must be greater than zero")
    with _connect(profile_root) as connection:
        strategy = _require_strategy(connection, strategy_id)
        version = _require_version(connection, strategy_version_id)
        if int(version["strategy_id"]) != strategy_id:
            raise DesktopServiceError(
                "strategy_version_mismatch",
                "Strategy version does not belong to the requested strategy.",
            )
        validation = _load_json(str(version["validation_json"]), "strategy validation")
        if not validation.get("can_execute"):
            raise DesktopServiceError(
                "strategy_validation_failed",
                "Strategy validation must pass before a backtest can run.",
            )
        dataset = resolve_governed_dataset(
            profile_root,
            asset_id=str(strategy["asset_id"]),
            timeframe=str(strategy["timeframe"]),
        )
        bars = _load_bars(dataset)
        result = _vectorized_backtest(
            bars,
            dsl=_load_json(str(version["dsl_json"]), "strategy DSL"),
            initial_cash=float(initial_cash),
            dataset=dataset,
            strategy_payload=_strategy_payload(connection, strategy_id, detail=False),
            version_payload=_version_payload(connection, strategy_version_id),
        )
        evidence_path = _write_result_evidence(profile_root, result)
        result = {**result, "evidence_path": str(evidence_path)}
        cursor = connection.execute(
            "INSERT INTO backtest_results(result_uuid, strategy_id, strategy_version_id, "
            "dataset_revision_id, result_json, result_digest, evidence_path) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                result["result_uuid"],
                strategy_id,
                strategy_version_id,
                str(dataset.dataset_revision_id),
                _json(result),
                result["result_digest"],
                str(evidence_path),
            ),
        )
        assert cursor.lastrowid is not None
        result_id = int(cursor.lastrowid)
        connection.execute(
            "UPDATE backtest_results SET result_json=? WHERE id=?",
            (_json({**result, "result_id": result_id}), result_id),
        )
        _append_event(
            connection,
            strategy_id,
            "backtest.completed",
            {"result_id": result_id, "result_digest": result["result_digest"]},
        )
        return _single_result(connection, result_id)


def get_backtest(profile_root: Path, result_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        return _single_result(connection, result_id)


def list_backtests(profile_root: Path, strategy_id: int | None = None) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        if strategy_id is None:
            rows = connection.execute("SELECT * FROM backtest_results ORDER BY id DESC").fetchall()
        else:
            rows = connection.execute(
                "SELECT * FROM backtest_results WHERE strategy_id=? ORDER BY id DESC",
                (strategy_id,),
            ).fetchall()
        return {
            "family": "osca.desktop-backtest-list.result",
            "version": "1.0.0",
            "results": [_result_payload(cast(sqlite3.Row, row)) for row in rows],
        }


def prepare_backtest_export(profile_root: Path, result_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        result = _result_payload(_require_result(connection, result_id))
        export_dir = profile_root / ".osca" / "desktop" / "exports" / "backtests"
        export_dir.mkdir(parents=True, exist_ok=True)
        equity_path = export_dir / f"backtest-{result_id}.equity.csv"
        trades_path = export_dir / f"backtest-{result_id}.trades.csv"
        _write_equity_csv(equity_path, cast(list[dict[str, Any]], result["equity_curve"]))
        _write_trades_csv(trades_path, cast(list[dict[str, Any]], result["trades"]))
        data_paths = [str(equity_path), str(trades_path)]
        body = {
            "family": "osca.desktop-backtest-manifest",
            "version": "1.0.0",
            "schema_version": _SCHEMA_VERSION,
            "result": result,
            "data_paths": data_paths,
            "self_contained_package": False,
            "provider_datasets_embedded": False,
        }
        digest = _sha256(_json(body).encode("utf-8"))
        manifest = {**body, "manifest_sha256": digest}
        path = export_dir / f"backtest-{result_id}.manifest.json"
        path.write_text(_pretty_json(manifest), encoding="utf-8")
        _append_event(
            connection,
            int(result["strategy_id"]),
            "backtest.exported",
            {"result_id": result_id, "manifest_sha256": digest},
        )
    return {
        "family": "osca.desktop-backtest-export.result",
        "version": "1.0.0",
        "result_id": result_id,
        "manifest_path": str(path),
        "manifest_sha256": digest,
        "data_paths": data_paths,
        "thin_manifest": True,
        "self_contained_package": False,
        "provider_datasets_embedded": False,
    }


def run_sensitivity(
    profile_root: Path,
    *,
    strategy_id: int,
    strategy_version_id: int,
    parameter: str,
    values: list[int],
    initial_cash: float = 10_000.0,
) -> dict[str, Any]:
    if parameter not in {"entry.window", "exit.window"}:
        raise DesktopServiceError(
            "invalid_parameters",
            "Sensitivity parameter must be entry.window or exit.window.",
        )
    normalized_values = _sensitivity_values(values)
    if initial_cash <= 0:
        raise DesktopServiceError("invalid_parameters", "initial_cash must be greater than zero")
    with _connect(profile_root) as connection:
        strategy = _require_strategy(connection, strategy_id)
        version = _require_version(connection, strategy_version_id)
        if int(version["strategy_id"]) != strategy_id:
            raise DesktopServiceError(
                "strategy_version_mismatch",
                "Strategy version does not belong to the requested strategy.",
            )
        dsl = _load_json(str(version["dsl_json"]), "strategy DSL")
        validation = _load_json(str(version["validation_json"]), "strategy validation")
        if not validation.get("can_execute"):
            raise DesktopServiceError(
                "strategy_validation_failed",
                "Strategy validation must pass before sensitivity can run.",
            )
        dataset = resolve_governed_dataset(
            profile_root,
            asset_id=str(strategy["asset_id"]),
            timeframe=str(strategy["timeframe"]),
        )
        bars = _load_bars(dataset)
        rows = []
        for value in normalized_values:
            scenario_dsl = _with_sensitivity_value(dsl, parameter, value)
            scenario_validation = validate_strategy_dsl(scenario_dsl)
            if not scenario_validation["can_execute"]:
                rows.append(
                    {
                        "parameter": parameter,
                        "value": value,
                        "status": "blocked",
                        "findings": scenario_validation["findings"],
                    }
                )
                continue
            result = _vectorized_backtest(
                bars,
                dsl=scenario_dsl,
                initial_cash=float(initial_cash),
                dataset=dataset,
                strategy_payload=_strategy_payload(connection, strategy_id, detail=False),
                version_payload=_version_payload(connection, strategy_version_id),
            )
            rows.append(
                {
                    "parameter": parameter,
                    "value": value,
                    "status": "completed",
                    "metrics": result["metrics"],
                    "result_digest": result["result_digest"],
                }
            )
        body = _evaluation_body(
            "sensitivity",
            strategy_id=strategy_id,
            strategy_version_id=strategy_version_id,
            dataset=dataset,
            payload={
                "budget": {
                    "max_scenarios": _MAX_SENSITIVITY_RUNS,
                    "requested_scenarios": len(normalized_values),
                    "completed_scenarios": sum(row["status"] == "completed" for row in rows),
                    "cancellation_supported": True,
                },
                "parameter": parameter,
                "values": normalized_values,
                "rows": rows,
                "warnings": [
                    "Sensitivity ranking is exploratory research evidence and may overfit "
                    "retained data."
                ],
            },
        )
        return _store_evaluation(profile_root, connection, body)


def run_walkforward(
    profile_root: Path,
    *,
    strategy_id: int,
    strategy_version_id: int,
    train_fraction: float = 0.6,
    initial_cash: float = 10_000.0,
) -> dict[str, Any]:
    if train_fraction <= 0 or train_fraction >= 1:
        raise DesktopServiceError(
            "invalid_parameters",
            "train_fraction must be greater than zero and less than one.",
        )
    if initial_cash <= 0:
        raise DesktopServiceError("invalid_parameters", "initial_cash must be greater than zero")
    with _connect(profile_root) as connection:
        strategy = _require_strategy(connection, strategy_id)
        version = _require_version(connection, strategy_version_id)
        if int(version["strategy_id"]) != strategy_id:
            raise DesktopServiceError(
                "strategy_version_mismatch",
                "Strategy version does not belong to the requested strategy.",
            )
        validation = _load_json(str(version["validation_json"]), "strategy validation")
        if not validation.get("can_execute"):
            raise DesktopServiceError(
                "strategy_validation_failed",
                "Strategy validation must pass before walk-forward can run.",
            )
        dataset = resolve_governed_dataset(
            profile_root,
            asset_id=str(strategy["asset_id"]),
            timeframe=str(strategy["timeframe"]),
        )
        bars = _load_bars(dataset)
        split = max(1, min(len(bars) - 1, int(len(bars) * train_fraction)))
        test_bars = bars[split:]
        dsl = _load_json(str(version["dsl_json"]), "strategy DSL")
        window = max(
            int(cast(dict[str, Any], dsl["entry"])["window"]),
            int(cast(dict[str, Any], dsl["exit"])["window"]),
        )
        if len(test_bars) < window + 2:
            raise DesktopServiceError(
                "walkforward_data_insufficient",
                "Walk-forward test partition requires enough observations for rule warmup.",
            )
        result = _vectorized_backtest(
            test_bars,
            dsl=dsl,
            initial_cash=float(initial_cash),
            dataset=dataset,
            strategy_payload=_strategy_payload(connection, strategy_id, detail=False),
            version_payload=_version_payload(connection, strategy_version_id),
        )
        body = _evaluation_body(
            "walkforward",
            strategy_id=strategy_id,
            strategy_version_id=strategy_version_id,
            dataset=dataset,
            payload={
                "budget": {
                    "max_partitions": 1,
                    "completed_partitions": 1,
                    "cancellation_supported": True,
                },
                "partitions": [
                    {
                        "train_start": bars[0].timestamp,
                        "train_end": bars[split - 1].timestamp,
                        "test_start": test_bars[0].timestamp,
                        "test_end": test_bars[-1].timestamp,
                        "train_rows": split,
                        "test_rows": len(test_bars),
                    }
                ],
                "rows": [
                    {
                        "partition": 1,
                        "status": "completed",
                        "metrics": result["metrics"],
                        "result_digest": result["result_digest"],
                    }
                ],
                "warnings": [
                    "Walk-forward result uses only the declared test partition for "
                    "reported metrics.",
                    "Parameter selection is not optimized in this first D7 evaluator.",
                ],
            },
        )
        return _store_evaluation(profile_root, connection, body)


def cancel_evaluation(profile_root: Path, evaluation_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        row = _require_evaluation(connection, evaluation_id)
        result = _load_json(str(row["result_json"]), "evaluation result")
        status = str(row["status"])
        if status in {"pending", "running"}:
            result = {
                **result,
                "status": "cancelled",
                "cancelled": True,
                "message": "Evaluation was cancelled before completion.",
            }
            connection.execute(
                "UPDATE backtest_evaluations SET status=?, result_json=? WHERE id=?",
                ("cancelled", _json(result), evaluation_id),
            )
        else:
            result = {
                **result,
                "cancelled": False,
                "message": "Evaluation already reached a terminal state.",
            }
        return {
            "family": "osca.desktop-backtest-cancel.result",
            "version": "1.0.0",
            "evaluation": {**result, "evaluation_id": evaluation_id},
        }


def _sensitivity_values(values: list[int]) -> list[int]:
    if not isinstance(values, list) or not values:
        raise DesktopServiceError(
            "invalid_parameters",
            "Sensitivity values must be a non-empty list.",
        )
    normalized: list[int] = []
    for value in values:
        if not isinstance(value, int) or isinstance(value, bool) or value < 2 or value > 252:
            raise DesktopServiceError(
                "invalid_parameters",
                "Sensitivity values must be integers from 2 through 252.",
            )
        if value not in normalized:
            normalized.append(value)
    if len(normalized) > _MAX_SENSITIVITY_RUNS:
        raise DesktopServiceError(
            "sensitivity_budget_exceeded",
            f"Sensitivity analysis is limited to {_MAX_SENSITIVITY_RUNS} scenarios.",
        )
    return normalized


def _with_sensitivity_value(dsl: dict[str, Any], parameter: str, value: int) -> dict[str, Any]:
    section_name, field_name = parameter.split(".", maxsplit=1)
    section = dict(cast(dict[str, Any], dsl[section_name]))
    section[field_name] = value
    return {**dsl, section_name: section}


def _evaluation_body(
    evaluation_type: str,
    *,
    strategy_id: int,
    strategy_version_id: int,
    dataset: GovernedDataset,
    payload: dict[str, Any],
) -> dict[str, Any]:
    stable_body = {
        "family": "osca.desktop-backtest-evaluation",
        "version": "1.0.0",
        "schema_version": _SCHEMA_VERSION,
        "status": "completed",
        "evaluation_type": evaluation_type,
        "strategy_id": strategy_id,
        "strategy_version_id": strategy_version_id,
        "source_dataset": {
            "dataset_revision_id": str(dataset.dataset_revision_id),
            "symbol": dataset.symbol,
            "timeframe": dataset.timeframe,
            "source_kind": dataset.source_kind,
            "retained_row_count": dataset.row_count,
        },
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "paper_orders_enabled": False,
        "real_capital_execution_enabled": False,
        **payload,
    }
    return {**stable_body, "result_digest": _sha256(_json(stable_body).encode("utf-8"))}


def _store_evaluation(
    profile_root: Path,
    connection: sqlite3.Connection,
    body: dict[str, Any],
) -> dict[str, Any]:
    result_uuid = str(uuid4())
    evidence_dir = profile_root / ".osca" / "desktop" / "backtests"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"{result_uuid}.evaluation.json"
    result = {**body, "result_uuid": result_uuid, "evidence_path": str(evidence_path)}
    evidence_path.write_text(_pretty_json(result), encoding="utf-8")
    cursor = connection.execute(
        "INSERT INTO backtest_evaluations(result_uuid, evaluation_type, status, strategy_id, "
        "strategy_version_id, dataset_revision_id, result_json, result_digest, evidence_path) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            result_uuid,
            result["evaluation_type"],
            result["status"],
            int(result["strategy_id"]),
            int(result["strategy_version_id"]),
            str(cast(dict[str, Any], result["source_dataset"])["dataset_revision_id"]),
            _json(result),
            result["result_digest"],
            str(evidence_path),
        ),
    )
    assert cursor.lastrowid is not None
    evaluation_id = int(cursor.lastrowid)
    connection.execute(
        "UPDATE backtest_evaluations SET result_json=? WHERE id=?",
        (_json({**result, "evaluation_id": evaluation_id}), evaluation_id),
    )
    _append_event(
        connection,
        int(result["strategy_id"]),
        f"backtest.{result['evaluation_type']}.completed",
        {"evaluation_id": evaluation_id, "result_digest": result["result_digest"]},
    )
    return {
        "family": "osca.desktop-backtest-evaluation.result",
        "version": "1.0.0",
        "evaluation": {**result, "evaluation_id": evaluation_id},
    }


def _vectorized_backtest(
    bars: list[_Bar],
    *,
    dsl: dict[str, Any],
    initial_cash: float,
    dataset: GovernedDataset,
    strategy_payload: dict[str, Any],
    version_payload: dict[str, Any],
) -> dict[str, Any]:
    entry_window = int(cast(dict[str, Any], dsl["entry"])["window"])
    exit_window = int(cast(dict[str, Any], dsl["exit"])["window"])
    window = max(entry_window, exit_window)
    if len(bars) < window + 2:
        raise DesktopServiceError(
            "backtest_data_insufficient",
            "Backtest requires enough observations for rule warmup and execution.",
        )
    closes = [bar.close for bar in bars]
    costs = cast(dict[str, Any], dsl.get("costs", {}))
    fees_bps = float(costs.get("fees_bps", 0.0))
    slippage_bps = float(costs.get("slippage_bps", 0.0))
    fraction = float(cast(dict[str, Any], dsl["sizing"])["fraction"])
    fee_rate = fees_bps / 10_000
    buy_price_multiplier = 1 + slippage_bps / 10_000
    sell_price_multiplier = 1 - slippage_bps / 10_000
    cash = initial_cash
    quantity = 0.0
    trades: list[dict[str, Any]] = []
    equity_curve: list[dict[str, Any]] = []
    max_equity = initial_cash
    max_drawdown = 0.0
    exposure_bars = 0
    signal_bars = 0
    for index, bar in enumerate(bars):
        entry_sma = _sma(closes, index, entry_window)
        exit_sma = _sma(closes, index, exit_window)
        signal = "warmup"
        if entry_sma is not None and exit_sma is not None:
            if quantity <= 0 and bar.close > entry_sma:
                signal = "buy"
                signal_bars += 1
                spend = cash * fraction
                fill_price = bar.close * buy_price_multiplier
                acquired = (spend * (1 - fee_rate)) / fill_price
                cash -= spend
                quantity += acquired
                trades.append(
                    {
                        "timestamp": bar.timestamp,
                        "side": "buy",
                        "fill_price": fill_price,
                        "quantity": acquired,
                        "fees": spend * fee_rate,
                        "research_assumption": True,
                    }
                )
            elif quantity > 0 and bar.close < exit_sma:
                signal = "sell"
                signal_bars += 1
                fill_price = bar.close * sell_price_multiplier
                gross = quantity * fill_price
                fees = gross * fee_rate
                cash += gross - fees
                trades.append(
                    {
                        "timestamp": bar.timestamp,
                        "side": "sell",
                        "fill_price": fill_price,
                        "quantity": quantity,
                        "fees": fees,
                        "research_assumption": True,
                    }
                )
                quantity = 0.0
            else:
                signal = "hold" if quantity > 0 else "flat"
        if quantity > 0:
            exposure_bars += 1
        equity = cash + quantity * bar.close
        max_equity = max(max_equity, equity)
        drawdown = (equity / max_equity) - 1 if max_equity else 0.0
        max_drawdown = min(max_drawdown, drawdown)
        equity_curve.append(
            {
                "timestamp": bar.timestamp,
                "close": bar.close,
                "equity": equity,
                "drawdown": drawdown,
                "signal": signal,
            }
        )
    final_equity = equity_curve[-1]["equity"]
    buy_and_hold_return = (bars[-1].close / bars[0].close) - 1
    stable_body = {
        "family": "osca.desktop-backtest-result",
        "version": "1.0.0",
        "schema_version": _SCHEMA_VERSION,
        "status": "completed",
        "fidelity_level": "vectorized_research",
        "execution_engine": "python.d7.vectorized_sma",
        "strategy": strategy_payload,
        "strategy_version": version_payload,
        "source_dataset": {
            "asset_id": strategy_payload["asset_id"],
            "symbol": dataset.symbol,
            "timeframe": dataset.timeframe,
            "dataset_revision_id": str(dataset.dataset_revision_id),
            "source_kind": dataset.source_kind,
            "source_attribution": dataset.source_attribution,
            "retained_row_count": dataset.row_count,
        },
        "assumptions": {
            "initial_cash": initial_cash,
            "fees_bps": fees_bps,
            "slippage_bps": slippage_bps,
            "sizing_fraction": fraction,
            "base_currency": "USD",
            "fidelity_disclosure": (
                "Vectorized research fill assumptions are not paper or live execution."
            ),
        },
        "metrics": {
            "bars_processed": len(bars),
            "signal_bar_count": signal_bars,
            "trade_count": len(trades),
            "exposure_bar_count": exposure_bars,
            "initial_cash": initial_cash,
            "final_equity": final_equity,
            "strategy_return": (final_equity / initial_cash) - 1,
            "buy_and_hold_return": buy_and_hold_return,
            "max_drawdown": max_drawdown,
        },
        "equity_curve": equity_curve,
        "trades": trades,
        "warnings": [
            "Research-only vectorized result; no broker, paper-order, live-order, "
            "or recommendation path exists."
        ],
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "paper_orders_enabled": False,
        "real_capital_execution_enabled": False,
    }
    digest = _sha256(_json(stable_body).encode("utf-8"))
    return {**stable_body, "result_uuid": str(uuid4()), "result_digest": digest}


def _load_bars(dataset: GovernedDataset) -> list[_Bar]:
    table = pq.read_table(dataset.payload_path)
    rows = table.to_pylist()
    bars = [
        _Bar(
            timestamp=str(row["timestamp"]),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
        )
        for row in rows
    ]
    if any(not bar.timestamp for bar in bars):
        raise DesktopServiceError(
            "backtest_data_invalid",
            "Backtest data contains missing timestamps.",
        )
    if [bar.timestamp for bar in bars] != sorted(bar.timestamp for bar in bars):
        raise DesktopServiceError(
            "backtest_data_invalid",
            "Backtest data timestamps must be sorted.",
        )
    if len({bar.timestamp for bar in bars}) != len(bars):
        raise DesktopServiceError(
            "backtest_data_invalid",
            "Backtest data timestamps must be unique.",
        )
    return bars


def _sma(closes: list[float], index: int, window: int) -> float | None:
    if index + 1 < window:
        return None
    values = closes[index + 1 - window : index + 1]
    return sum(values) / window


def _write_result_evidence(profile_root: Path, result: dict[str, Any]) -> Path:
    evidence_dir = profile_root / ".osca" / "desktop" / "backtests"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{result['result_uuid']}.json"
    path.write_text(_pretty_json(result), encoding="utf-8")
    return path


def _write_equity_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["timestamp", "close", "equity", "drawdown", "signal"],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _write_trades_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "timestamp",
                "side",
                "fill_price",
                "quantity",
                "fees",
                "research_assumption",
            ],
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _database(profile_root: Path) -> Path:
    if not profile_root.is_absolute() or not profile_root.is_dir():
        raise DesktopServiceError(
            "profile_unavailable",
            "A valid absolute profile directory is required.",
        )
    directory = profile_root / ".osca" / "desktop"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "d7-strategies.sqlite3"


def _connect(profile_root: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(_database(profile_root))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    current_row = connection.execute("PRAGMA user_version").fetchone()
    current = int(cast(tuple[int], current_row)[0])
    if current > _SCHEMA_VERSION:
        connection.close()
        raise DesktopServiceError(
            "strategy_schema_newer",
            "Strategy data was created by a newer OSCA version.",
        )
    if current == 0:
        connection.executescript(
            """
            CREATE TABLE strategies(
              id INTEGER PRIMARY KEY,
              strategy_uuid TEXT NOT NULL UNIQUE,
              name TEXT NOT NULL COLLATE NOCASE UNIQUE,
              objective TEXT NOT NULL,
              asset_id TEXT NOT NULL,
              timeframe TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'active'
                CHECK(status IN ('active', 'archived')),
              current_version_id INTEGER,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE strategy_versions(
              id INTEGER PRIMARY KEY,
              version_uuid TEXT NOT NULL UNIQUE,
              strategy_id INTEGER NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
              version_number INTEGER NOT NULL,
              dsl_json TEXT NOT NULL,
              dsl_digest TEXT NOT NULL,
              validation_json TEXT NOT NULL,
              summary TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              UNIQUE(strategy_id, version_number)
            );
            CREATE TABLE strategy_timeline(
              id INTEGER PRIMARY KEY,
              strategy_id INTEGER NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
              event_type TEXT NOT NULL,
              details_json TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE backtest_results(
              id INTEGER PRIMARY KEY,
              result_uuid TEXT NOT NULL UNIQUE,
              strategy_id INTEGER NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
              strategy_version_id INTEGER NOT NULL
                REFERENCES strategy_versions(id) ON DELETE CASCADE,
              dataset_revision_id TEXT NOT NULL,
              result_json TEXT NOT NULL,
              result_digest TEXT NOT NULL,
              evidence_path TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            """
        )
        current = 1
    if current == 1:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS backtest_evaluations(
              id INTEGER PRIMARY KEY,
              result_uuid TEXT NOT NULL UNIQUE,
              evaluation_type TEXT NOT NULL
                CHECK(evaluation_type IN ('sensitivity', 'walkforward')),
              status TEXT NOT NULL
                CHECK(status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
              strategy_id INTEGER NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
              strategy_version_id INTEGER NOT NULL
                REFERENCES strategy_versions(id) ON DELETE CASCADE,
              dataset_revision_id TEXT NOT NULL,
              result_json TEXT NOT NULL,
              result_digest TEXT NOT NULL,
              evidence_path TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            PRAGMA user_version=2;
            """
        )
    return connection


def _insert_version(
    connection: sqlite3.Connection,
    *,
    strategy_id: int,
    version_uuid: str,
    version_number: int,
    dsl: dict[str, Any],
    validation: dict[str, Any],
    summary: str,
) -> int:
    encoded = _json(dsl)
    cursor = connection.execute(
        "INSERT INTO strategy_versions(version_uuid, strategy_id, version_number, dsl_json, "
        "dsl_digest, validation_json, summary) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            version_uuid,
            strategy_id,
            version_number,
            encoded,
            _sha256(encoded.encode("utf-8")),
            _json(validation),
            summary,
        ),
    )
    assert cursor.lastrowid is not None
    return int(cursor.lastrowid)


def _single_strategy(connection: sqlite3.Connection, strategy_id: int) -> dict[str, Any]:
    return {
        "family": "osca.desktop-strategy.result",
        "version": "1.0.0",
        "strategy": _strategy_payload(connection, strategy_id),
    }


def _strategy_payload(
    connection: sqlite3.Connection,
    strategy_id: int,
    *,
    detail: bool = True,
) -> dict[str, Any]:
    row = _require_strategy(connection, strategy_id)
    versions = [
        _version_payload(connection, int(version["id"]))
        for version in connection.execute(
            "SELECT id FROM strategy_versions WHERE strategy_id=? ORDER BY version_number",
            (strategy_id,),
        )
    ]
    current_version = (
        _version_payload(connection, int(row["current_version_id"]))
        if row["current_version_id"] is not None
        else None
    )
    payload = {
        "strategy_id": int(row["id"]),
        "strategy_uuid": str(row["strategy_uuid"]),
        "name": str(row["name"]),
        "objective": str(row["objective"]),
        "asset_id": str(row["asset_id"]),
        "timeframe": str(row["timeframe"]),
        "status": str(row["status"]),
        "current_version": current_version,
        "version_count": len(versions),
        "created_at": str(row["created_at"]),
        "updated_at": str(row["updated_at"]),
    }
    if detail:
        payload["versions"] = versions
        payload["timeline"] = [
            _event_payload(cast(sqlite3.Row, event))
            for event in connection.execute(
                "SELECT * FROM strategy_timeline WHERE strategy_id=? ORDER BY id",
                (strategy_id,),
            )
        ]
    return payload


def _version_payload(connection: sqlite3.Connection, version_id: int) -> dict[str, Any]:
    row = _require_version(connection, version_id)
    return {
        "version_id": int(row["id"]),
        "version_uuid": str(row["version_uuid"]),
        "strategy_id": int(row["strategy_id"]),
        "version_number": int(row["version_number"]),
        "dsl": _load_json(str(row["dsl_json"]), "strategy DSL"),
        "dsl_digest": str(row["dsl_digest"]),
        "validation": _load_json(str(row["validation_json"]), "strategy validation"),
        "summary": str(row["summary"]),
        "created_at": str(row["created_at"]),
    }


def _single_result(connection: sqlite3.Connection, result_id: int) -> dict[str, Any]:
    return {
        "family": "osca.desktop-backtest.result",
        "version": "1.0.0",
        "result": _result_payload(_require_result(connection, result_id)),
    }


def _result_payload(row: sqlite3.Row) -> dict[str, Any]:
    result = _load_json(str(row["result_json"]), "backtest result")
    result["result_id"] = int(row["id"])
    result["strategy_id"] = int(row["strategy_id"])
    result["strategy_version_id"] = int(row["strategy_version_id"])
    result["dataset_revision_id"] = str(row["dataset_revision_id"])
    result["result_digest"] = str(row["result_digest"])
    result["evidence_path"] = str(row["evidence_path"])
    result["created_at"] = str(row["created_at"])
    return result


def _require_strategy(connection: sqlite3.Connection, strategy_id: int) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM strategies WHERE id=?", (strategy_id,)).fetchone()
    if row is None:
        raise DesktopServiceError("strategy_not_found", "Strategy was not found.")
    return cast(sqlite3.Row, row)


def _require_mutable_strategy(connection: sqlite3.Connection, strategy_id: int) -> sqlite3.Row:
    row = _require_strategy(connection, strategy_id)
    if row["status"] != "active":
        raise DesktopServiceError("strategy_not_mutable", "Strategy is not active.")
    return row


def _require_version(connection: sqlite3.Connection, version_id: int) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM strategy_versions WHERE id=?", (version_id,)).fetchone()
    if row is None:
        raise DesktopServiceError("strategy_version_not_found", "Strategy version was not found.")
    return cast(sqlite3.Row, row)


def _require_result(connection: sqlite3.Connection, result_id: int) -> sqlite3.Row:
    row = connection.execute("SELECT * FROM backtest_results WHERE id=?", (result_id,)).fetchone()
    if row is None:
        raise DesktopServiceError("backtest_not_found", "Backtest result was not found.")
    return cast(sqlite3.Row, row)


def _require_evaluation(connection: sqlite3.Connection, evaluation_id: int) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM backtest_evaluations WHERE id=?",
        (evaluation_id,),
    ).fetchone()
    if row is None:
        raise DesktopServiceError("evaluation_not_found", "Backtest evaluation was not found.")
    return cast(sqlite3.Row, row)


def _append_event(
    connection: sqlite3.Connection,
    strategy_id: int,
    event_type: str,
    details: dict[str, Any],
) -> None:
    connection.execute(
        "INSERT INTO strategy_timeline(strategy_id, event_type, details_json) VALUES (?, ?, ?)",
        (strategy_id, event_type, _json(details)),
    )


def _event_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "event_id": int(row["id"]),
        "strategy_id": int(row["strategy_id"]),
        "event_type": str(row["event_type"]),
        "details": _load_json(str(row["details_json"]), "timeline details"),
        "created_at": str(row["created_at"]),
    }


def _find_forbidden(value: Any, findings: list[dict[str, str]]) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            lowered = str(key).lower()
            if lowered in _FORBIDDEN_KEYS:
                findings.append(
                    _finding("executable_field", "error", f"Forbidden executable field: {key}.")
                )
                return
            _find_forbidden(nested, findings)
    elif isinstance(value, list):
        for item in value:
            _find_forbidden(item, findings)


def _finding(code: str, severity: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


def _strategy_summary(dsl: dict[str, Any]) -> str:
    entry = cast(dict[str, Any], dsl.get("entry", {}))
    exit_rule = cast(dict[str, Any], dsl.get("exit", {}))
    return (
        f"Entry {entry.get('type', 'unknown')} window {entry.get('window', 'n/a')}; "
        f"exit {exit_rule.get('type', 'unknown')} window {exit_rule.get('window', 'n/a')}."
    )


def _safe_json_object(value: dict[str, Any], label: str, *, limit: int) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DesktopServiceError("invalid_parameters", f"{label} must be an object.")
    encoded = _json(value)
    if len(encoded.encode("utf-8")) > limit:
        raise DesktopServiceError("invalid_parameters", f"{label} is too large.")
    return value


def _bounded_text(value: str | None, label: str, *, limit: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{label} must be a non-empty string up to {limit} characters.",
        )
    return value.strip()


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _pretty_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n"


def _load_json(value: str, label: str) -> dict[str, Any]:
    loaded = json.loads(value)
    if not isinstance(loaded, dict):
        raise DesktopServiceError("invalid_state", f"{label} is not an object.")
    return cast(dict[str, Any], loaded)


def _sha256(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()
