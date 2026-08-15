"""D7 strategy-builder and backtest-lab desktop application methods."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from osca.desktop_api.d6_service import D6DesktopApplicationService
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopServiceError
from osca.desktop_api.strategies import (
    cancel_evaluation,
    create_strategy,
    create_strategy_version,
    get_backtest,
    get_strategy,
    list_backtests,
    list_strategies,
    prepare_backtest_export,
    run_backtest,
    run_sensitivity,
    run_walkforward,
    validate_strategy_dsl,
)


class D7DesktopApplicationService(D6DesktopApplicationService):
    """Extend D6 with narrow strategy and backtest research methods."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._handlers.update(
            {
                "strategy.create": self._strategy_create,
                "strategy.list": self._strategy_list,
                "strategy.get": self._strategy_get,
                "strategy.version.create": self._strategy_version_create,
                "strategy.validate": self._strategy_validate,
                "backtest.run": self._backtest_run,
                "backtest.cancel": self._backtest_cancel,
                "backtest.get": self._backtest_get,
                "backtest.list": self._backtest_list,
                "backtest.export.prepare": self._backtest_export_prepare,
                "backtest.sensitivity.run": self._backtest_sensitivity_run,
                "backtest.walkforward.run": self._backtest_walkforward_run,
            }
        )

    def _strategy_create(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "name", "objective", "asset_id", "timeframe", "dsl"},
            "strategy.create",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return create_strategy(
                profile_root,
                name=_required_text(params, "name"),
                objective=_required_text(params, "objective", limit=1000),
                asset_id=_required_text(params, "asset_id", limit=128),
                timeframe=_required_text(params, "timeframe", limit=20),
                dsl=_required_object(params, "dsl"),
            )

    def _strategy_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "include_archived"}, "strategy.list")
        return list_strategies(
            _required_path(params, "profile_root"),
            include_archived=_optional_bool(params, "include_archived", False),
        )

    def _strategy_get(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "strategy_id"}, "strategy.get")
        return get_strategy(
            _required_path(params, "profile_root"),
            _required_int(params, "strategy_id"),
        )

    def _strategy_version_create(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "strategy_id", "dsl", "summary"},
            "strategy.version.create",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return create_strategy_version(
                profile_root,
                strategy_id=_required_int(params, "strategy_id"),
                dsl=_required_object(params, "dsl"),
                summary=_optional_text(params, "summary", limit=240),
            )

    def _strategy_validate(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "dsl"}, "strategy.validate")
        _required_path(params, "profile_root")
        return {
            "family": "osca.desktop-strategy-validate.result",
            "version": "1.0.0",
            "validation": validate_strategy_dsl(_required_object(params, "dsl")),
        }

    def _backtest_run(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "strategy_id", "strategy_version_id", "initial_cash"},
            "backtest.run",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return run_backtest(
                profile_root,
                strategy_id=_required_int(params, "strategy_id"),
                strategy_version_id=_required_int(params, "strategy_version_id"),
                initial_cash=_optional_float(params, "initial_cash", 10_000.0),
            )

    def _backtest_get(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "result_id"}, "backtest.get")
        return get_backtest(
            _required_path(params, "profile_root"),
            _required_int(params, "result_id"),
        )

    def _backtest_cancel(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "evaluation_id"}, "backtest.cancel")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return cancel_evaluation(
                profile_root,
                _required_int(params, "evaluation_id"),
            )

    def _backtest_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "strategy_id"}, "backtest.list")
        return list_backtests(
            _required_path(params, "profile_root"),
            strategy_id=_optional_int(params, "strategy_id"),
        )

    def _backtest_export_prepare(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "result_id"}, "backtest.export.prepare")
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return prepare_backtest_export(
                profile_root,
                _required_int(params, "result_id"),
            )

    def _backtest_sensitivity_run(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "strategy_id",
                "strategy_version_id",
                "parameter",
                "values",
                "initial_cash",
            },
            "backtest.sensitivity.run",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return run_sensitivity(
                profile_root,
                strategy_id=_required_int(params, "strategy_id"),
                strategy_version_id=_required_int(params, "strategy_version_id"),
                parameter=_required_text(params, "parameter", limit=32),
                values=_required_int_list(params, "values"),
                initial_cash=_optional_float(params, "initial_cash", 10_000.0),
            )

    def _backtest_walkforward_run(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "strategy_id",
                "strategy_version_id",
                "train_fraction",
                "initial_cash",
            },
            "backtest.walkforward.run",
        )
        profile_root = _required_path(params, "profile_root")
        with ProfileMutationLock(profile_root):
            return run_walkforward(
                profile_root,
                strategy_id=_required_int(params, "strategy_id"),
                strategy_version_id=_required_int(params, "strategy_version_id"),
                train_fraction=_optional_float(params, "train_fraction", 0.5),
                initial_cash=_optional_float(params, "initial_cash", 10_000.0),
            )


def _allowed(params: dict[str, Any], allowed: set[str], method: str) -> None:
    unexpected = sorted(set(params) - allowed)
    if unexpected:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{method} received unsupported parameters: {', '.join(unexpected)}",
        )


def _required_path(params: dict[str, Any], name: str) -> Path:
    path = Path(_required_text(params, name)).expanduser()
    if not path.is_absolute():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an absolute path")
    return path.resolve()


def _required_text(params: dict[str, Any], name: str, *, limit: int = 256) -> str:
    value = params.get(name)
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must be a non-empty string up to {limit} characters",
        )
    return value.strip()


def _optional_text(
    params: dict[str, Any],
    name: str,
    *,
    limit: int = 256,
) -> str | None:
    if name not in params or params[name] is None:
        return None
    return _required_text(params, name, limit=limit)


def _required_int(params: dict[str, Any], name: str) -> int:
    value = params.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise DesktopServiceError("invalid_parameters", f"{name} must be a positive integer")
    return value


def _optional_int(params: dict[str, Any], name: str) -> int | None:
    if name not in params or params[name] is None:
        return None
    return _required_int(params, name)


def _optional_bool(params: dict[str, Any], name: str, default: bool) -> bool:
    if name not in params or params[name] is None:
        return default
    value = params[name]
    if not isinstance(value, bool):
        raise DesktopServiceError("invalid_parameters", f"{name} must be a boolean")
    return value


def _optional_float(params: dict[str, Any], name: str, default: float) -> float:
    if name not in params or params[name] is None:
        return default
    value = params[name]
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise DesktopServiceError("invalid_parameters", f"{name} must be numeric")
    return float(value)


def _required_int_list(params: dict[str, Any], name: str) -> list[int]:
    value = params.get(name)
    if not isinstance(value, list):
        raise DesktopServiceError("invalid_parameters", f"{name} must be a list")
    result: list[int] = []
    for item in value:
        if not isinstance(item, int) or isinstance(item, bool):
            raise DesktopServiceError(
                "invalid_parameters",
                f"{name} must contain only integers",
            )
        result.append(item)
    return result


def _required_object(params: dict[str, Any], name: str) -> dict[str, Any]:
    value = params.get(name)
    if not isinstance(value, dict):
        raise DesktopServiceError("invalid_parameters", f"{name} must be an object")
    return value
