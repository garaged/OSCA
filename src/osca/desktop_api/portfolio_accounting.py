"""D8 semantic desktop adapter for virtual-portfolio accounting."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from pathlib import Path
from typing import Any, TypeVar
from uuid import UUID

from osca.desktop_api.d7_service import D7DesktopApplicationService
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopServiceError
from osca.paper import (
    AccountingConflictError,
    AccountingNotFoundError,
    AccountingPersistenceError,
    PortfolioAccountingService,
    ValuationObservation,
    clone_portfolio,
    export_portfolio_bundle,
    read_portfolio_bundle,
    reset_portfolio,
    restore_portfolio_bundle,
    write_portfolio_bundle,
)

T = TypeVar("T")


class PortfolioAccountingDesktopService(D7DesktopApplicationService):
    """Extend D7 with research-only virtual-portfolio accounting methods."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._handlers.update(
            {
                "portfolio.create": self._portfolio_create,
                "portfolio.list": self._portfolio_list,
                "portfolio.get": self._portfolio_get,
                "portfolio.acquisition.record": self._acquisition_record,
                "portfolio.disposal.record": self._disposal_record,
                "portfolio.dividend.record": self._dividend_record,
                "portfolio.split.record": self._split_record,
                "portfolio.fork.record": self._fork_record,
                "portfolio.fx.record": self._fx_record,
                "portfolio.reversal.record": self._reversal_record,
                "portfolio.valuation.record": self._valuation_record,
                "portfolio.clone": self._portfolio_clone,
                "portfolio.reset": self._portfolio_reset,
                "portfolio.export.prepare": self._portfolio_export_prepare,
                "portfolio.restore": self._portfolio_restore,
            }
        )

    def _portfolio_create(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "name", "base_currency", "starting_cash"},
            "portfolio.create",
        )
        profile_root = _required_path(params, "profile_root")
        service = _accounting_service(profile_root)
        with ProfileMutationLock(profile_root):
            portfolio = _domain_call(
                lambda: service.create_portfolio(
                    name=_required_text(params, "name", limit=120),
                    base_currency=_optional_text(params, "base_currency", "USD", limit=3),
                    starting_cash=_optional_decimal(params, "starting_cash", Decimal("10000")),
                )
            )
        return _portfolio_result(service, portfolio.portfolio_id)

    def _portfolio_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root"}, "portfolio.list")
        service = _accounting_service(_required_path(params, "profile_root"))
        portfolios = _domain_call(service.list_portfolios)
        return {
            "family": "osca.desktop-portfolio-list.result",
            "version": "1.0.0",
            "portfolios": [item.model_dump(mode="json") for item in portfolios],
            "network_access_enabled": False,
            "recommendations_enabled": False,
            "real_capital_execution_enabled": False,
        }

    def _portfolio_get(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "portfolio_id"}, "portfolio.get")
        service = _accounting_service(_required_path(params, "profile_root"))
        return _portfolio_result(service, _required_uuid(params, "portfolio_id"), include_evidence=True)

    def _acquisition_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "portfolio_id",
                "instrument_id",
                "quantity",
                "unit_price",
                "currency",
                "fee",
                "source_id",
            },
            "portfolio.acquisition.record",
        )
        return self._mutate(
            params,
            lambda service, portfolio_id: service.record_acquisition(
                portfolio_id,
                instrument_id=_required_text(params, "instrument_id", limit=200),
                quantity=_required_decimal(params, "quantity"),
                unit_price=_required_decimal(params, "unit_price"),
                currency=_required_text(params, "currency", limit=3),
                fee=_optional_decimal(params, "fee", Decimal("0")),
                source_id=_required_text(params, "source_id", limit=200),
            ),
        )

    def _disposal_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "portfolio_id",
                "instrument_id",
                "quantity",
                "unit_price",
                "currency",
                "fee",
                "source_id",
                "lot_allocations",
            },
            "portfolio.disposal.record",
        )
        allocations = _optional_lot_allocations(params)
        return self._mutate(
            params,
            lambda service, portfolio_id: service.record_disposal(
                portfolio_id,
                instrument_id=_required_text(params, "instrument_id", limit=200),
                quantity=_required_decimal(params, "quantity"),
                unit_price=_required_decimal(params, "unit_price"),
                currency=_required_text(params, "currency", limit=3),
                fee=_optional_decimal(params, "fee", Decimal("0")),
                lot_allocations=allocations,
                source_id=_required_text(params, "source_id", limit=200),
            ),
        )

    def _dividend_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "portfolio_id", "instrument_id", "amount", "currency", "source_id"},
            "portfolio.dividend.record",
        )
        return self._mutate(
            params,
            lambda service, portfolio_id: service.record_dividend(
                portfolio_id,
                instrument_id=_required_text(params, "instrument_id", limit=200),
                amount=_required_decimal(params, "amount"),
                currency=_required_text(params, "currency", limit=3),
                source_id=_required_text(params, "source_id", limit=200),
            ),
        )

    def _split_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "portfolio_id", "instrument_id", "factor", "source_id"},
            "portfolio.split.record",
        )
        return self._mutate(
            params,
            lambda service, portfolio_id: service.record_split(
                portfolio_id,
                instrument_id=_required_text(params, "instrument_id", limit=200),
                factor=_required_decimal(params, "factor"),
                source_id=_required_text(params, "source_id", limit=200),
            ),
        )

    def _fork_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "portfolio_id",
                "source_instrument_id",
                "new_instrument_id",
                "new_quantity",
                "currency",
                "allocated_book_cost",
                "source_lot_allocations",
                "source_id",
            },
            "portfolio.fork.record",
        )
        source_allocations = _optional_lot_allocations(
            params,
            name="source_lot_allocations",
        )
        return self._mutate(
            params,
            lambda service, portfolio_id: service.record_fork(
                portfolio_id,
                source_instrument_id=_required_text(
                    params, "source_instrument_id", limit=200
                ),
                new_instrument_id=_required_text(params, "new_instrument_id", limit=200),
                new_quantity=_required_decimal(params, "new_quantity"),
                currency=_required_text(params, "currency", limit=3),
                allocated_book_cost=_optional_decimal(
                    params, "allocated_book_cost", Decimal("0")
                ),
                source_lot_allocations=source_allocations,
                source_id=_required_text(params, "source_id", limit=200),
            ),
        )

    def _fx_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "portfolio_id",
                "from_currency",
                "from_amount",
                "to_currency",
                "to_amount",
                "source_id",
            },
            "portfolio.fx.record",
        )
        return self._mutate(
            params,
            lambda service, portfolio_id: service.record_fx_conversion(
                portfolio_id,
                from_currency=_required_text(params, "from_currency", limit=3),
                from_amount=_required_decimal(params, "from_amount"),
                to_currency=_required_text(params, "to_currency", limit=3),
                to_amount=_required_decimal(params, "to_amount"),
                source_id=_required_text(params, "source_id", limit=200),
            ),
        )

    def _reversal_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "portfolio_id", "original_event_id", "reason", "source_id"},
            "portfolio.reversal.record",
        )
        return self._mutate(
            params,
            lambda service, portfolio_id: service.reverse_event(
                portfolio_id,
                original_event_id=_required_uuid(params, "original_event_id"),
                reason=_required_text(params, "reason", limit=500),
                source_id=_required_text(params, "source_id", limit=200),
            ),
        )

    def _valuation_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "portfolio_id",
                "asset_id",
                "quantity",
                "unit_price",
                "price_currency",
                "price_source",
                "price_effective_at",
                "fx_rate_to_base",
                "fx_source",
                "fx_effective_at",
                "valuation_revision",
            },
            "portfolio.valuation.record",
        )
        profile_root = _required_path(params, "profile_root")
        portfolio_id = _required_uuid(params, "portfolio_id")
        service = _accounting_service(profile_root)
        observation = ValuationObservation(
            portfolio_id=portfolio_id,
            asset_id=_required_text(params, "asset_id", limit=200),
            quantity=_required_decimal(params, "quantity"),
            unit_price=_required_decimal(params, "unit_price"),
            price_currency=_required_text(params, "price_currency", limit=3),
            price_source=_required_text(params, "price_source", limit=200),
            price_effective_at=_required_datetime(params, "price_effective_at"),
            fx_rate_to_base=_optional_decimal_or_none(params, "fx_rate_to_base"),
            fx_source=_optional_text_or_none(params, "fx_source", limit=200),
            fx_effective_at=_optional_datetime(params, "fx_effective_at"),
            valuation_revision=_required_text(params, "valuation_revision", limit=200),
        )
        with ProfileMutationLock(profile_root):
            _domain_call(lambda: service.append_valuation(observation))
        return _portfolio_result(service, portfolio_id)

    def _portfolio_clone(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "portfolio_id", "name"}, "portfolio.clone")
        profile_root = _required_path(params, "profile_root")
        service = _accounting_service(profile_root)
        source_id = _required_uuid(params, "portfolio_id")
        with ProfileMutationLock(profile_root):
            portfolio = _domain_call(
                lambda: clone_portfolio(
                    service,
                    source_id,
                    name=_required_text(params, "name", limit=120),
                )
            )
        return _portfolio_result(service, portfolio.portfolio_id)

    def _portfolio_reset(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "portfolio_id", "name", "starting_cash"},
            "portfolio.reset",
        )
        profile_root = _required_path(params, "profile_root")
        service = _accounting_service(profile_root)
        source_id = _required_uuid(params, "portfolio_id")
        with ProfileMutationLock(profile_root):
            portfolio = _domain_call(
                lambda: reset_portfolio(
                    service,
                    source_id,
                    name=_required_text(params, "name", limit=120),
                    starting_cash=_optional_decimal(
                        params, "starting_cash", Decimal("10000")
                    ),
                )
            )
        return _portfolio_result(service, portfolio.portfolio_id)

    def _portfolio_export_prepare(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "portfolio_id"},
            "portfolio.export.prepare",
        )
        profile_root = _required_path(params, "profile_root")
        portfolio_id = _required_uuid(params, "portfolio_id")
        service = _accounting_service(profile_root)
        with ProfileMutationLock(profile_root):
            bundle = _domain_call(lambda: export_portfolio_bundle(service, portfolio_id))
            output_path = (
                profile_root
                / "exports"
                / "virtual-portfolios"
                / f"{portfolio_id}.portfolio.json"
            )
            _domain_call(lambda: write_portfolio_bundle(bundle, output_path))
        return {
            "family": "osca.desktop-portfolio-export.result",
            "version": "1.0.0",
            "portfolio_id": str(portfolio_id),
            "output_path": str(output_path),
            "content_digest": bundle.content_digest,
            "provider_data_embedded": False,
        }

    def _portfolio_restore(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root", "input_path"}, "portfolio.restore")
        profile_root = _required_path(params, "profile_root")
        input_path = _required_existing_file(params, "input_path")
        service = _accounting_service(profile_root)
        bundle = _domain_call(lambda: read_portfolio_bundle(input_path))
        with ProfileMutationLock(profile_root):
            portfolio = _domain_call(
                lambda: restore_portfolio_bundle(service.store, bundle)
            )
        return _portfolio_result(service, portfolio.portfolio_id, include_evidence=True)

    def _mutate(
        self,
        params: dict[str, Any],
        operation: Callable[[PortfolioAccountingService, UUID], object],
    ) -> dict[str, Any]:
        profile_root = _required_path(params, "profile_root")
        portfolio_id = _required_uuid(params, "portfolio_id")
        service = _accounting_service(profile_root)
        with ProfileMutationLock(profile_root):
            _domain_call(lambda: operation(service, portfolio_id))
        return _portfolio_result(service, portfolio_id)


def _portfolio_result(
    service: PortfolioAccountingService,
    portfolio_id: UUID,
    *,
    include_evidence: bool = False,
) -> dict[str, Any]:
    portfolio = _domain_call(lambda: service.get_portfolio(portfolio_id))
    projection = _domain_call(lambda: service.project(portfolio_id))
    result: dict[str, Any] = {
        "family": "osca.desktop-portfolio.result",
        "version": "1.0.0",
        "portfolio": portfolio.model_dump(mode="json"),
        "projection": projection.model_dump(mode="json"),
        "network_access_enabled": False,
        "recommendations_enabled": False,
        "broker_connections_enabled": False,
        "autonomous_execution_enabled": False,
        "live_order_execution": False,
        "real_capital_execution_enabled": False,
    }
    if include_evidence:
        result["events"] = [
            item.model_dump(mode="json") for item in _domain_call(lambda: service.events(portfolio_id))
        ]
        result["journal"] = [
            item.model_dump(mode="json")
            for item in _domain_call(lambda: service.journal(portfolio_id))
        ]
        result["valuations"] = [
            item.model_dump(mode="json")
            for item in _domain_call(lambda: service.valuations(portfolio_id))
        ]
    return result


def _accounting_service(profile_root: Path) -> PortfolioAccountingService:
    if not profile_root.is_dir():
        raise DesktopServiceError(
            "profile_not_found",
            f"profile directory does not exist: {profile_root}",
        )
    return _domain_call(lambda: PortfolioAccountingService.for_profile(profile_root))


def _domain_call(operation: Callable[[], T]) -> T:
    try:
        return operation()
    except AccountingConflictError as exc:
        raise DesktopServiceError("portfolio_conflict", str(exc)) from exc
    except AccountingNotFoundError as exc:
        raise DesktopServiceError("portfolio_not_found", str(exc)) from exc
    except AccountingPersistenceError as exc:
        raise DesktopServiceError("portfolio_storage_error", str(exc)) from exc


def _allowed(params: dict[str, Any], allowed: set[str], method: str) -> None:
    unexpected = sorted(set(params) - allowed)
    if unexpected:
        raise DesktopServiceError(
            "invalid_parameters",
            f"{method} received unsupported parameters: {', '.join(unexpected)}",
        )


def _required_path(params: dict[str, Any], name: str) -> Path:
    raw = _required_text(params, name, limit=4096)
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an absolute path")
    return path.resolve()


def _required_existing_file(params: dict[str, Any], name: str) -> Path:
    path = _required_path(params, name)
    if not path.is_file():
        raise DesktopServiceError("invalid_parameters", f"{name} must be an existing file")
    return path


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
    default: str,
    *,
    limit: int,
) -> str:
    if name not in params or params[name] is None:
        return default
    return _required_text(params, name, limit=limit)


def _optional_text_or_none(
    params: dict[str, Any],
    name: str,
    *,
    limit: int,
) -> str | None:
    if name not in params or params[name] is None:
        return None
    return _required_text(params, name, limit=limit)


def _required_uuid(params: dict[str, Any], name: str) -> UUID:
    raw = _required_text(params, name, limit=64)
    try:
        return UUID(raw)
    except ValueError as exc:
        raise DesktopServiceError("invalid_parameters", f"{name} must be a UUID") from exc


def _decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise DesktopServiceError(
            "invalid_parameters",
            f"{name} must be supplied as an exact decimal string or integer",
        )
    try:
        result = Decimal(str(value).strip())
    except Exception as exc:
        raise DesktopServiceError("invalid_parameters", f"{name} is not a decimal") from exc
    if not result.is_finite():
        raise DesktopServiceError("invalid_parameters", f"{name} must be finite")
    return result


def _required_decimal(params: dict[str, Any], name: str) -> Decimal:
    if name not in params:
        raise DesktopServiceError("invalid_parameters", f"{name} is required")
    return _decimal(params[name], name)


def _optional_decimal(params: dict[str, Any], name: str, default: Decimal) -> Decimal:
    if name not in params or params[name] is None:
        return default
    return _decimal(params[name], name)


def _optional_decimal_or_none(params: dict[str, Any], name: str) -> Decimal | None:
    if name not in params or params[name] is None:
        return None
    return _decimal(params[name], name)


def _required_datetime(params: dict[str, Any], name: str):
    raw = _required_text(params, name, limit=64)
    from datetime import datetime

    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DesktopServiceError("invalid_parameters", f"{name} must be ISO-8601") from exc
    if value.tzinfo is None or value.utcoffset() is None:
        raise DesktopServiceError("invalid_parameters", f"{name} must include a timezone")
    return value


def _optional_datetime(params: dict[str, Any], name: str):
    if name not in params or params[name] is None:
        return None
    return _required_datetime(params, name)


def _optional_lot_allocations(
    params: dict[str, Any],
    *,
    name: str = "lot_allocations",
) -> dict[UUID, Decimal] | None:
    raw = params.get(name)
    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise DesktopServiceError("invalid_parameters", f"{name} must be an object")
    allocations: dict[UUID, Decimal] = {}
    for lot_id, quantity in raw.items():
        if not isinstance(lot_id, str):
            raise DesktopServiceError("invalid_parameters", f"{name} keys must be UUID strings")
        try:
            identifier = UUID(lot_id)
        except ValueError as exc:
            raise DesktopServiceError(
                "invalid_parameters", f"{name} keys must be UUID strings"
            ) from exc
        allocations[identifier] = _decimal(quantity, f"{name}.{lot_id}")
    return allocations
