"""Desktop composition that binds D9 simulation to retained M8 paper-account controls."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from osca.desktop_api import paper_forward
from osca.desktop_api.portfolio_accounting import _allowed
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopServiceError
from osca.paper.contracts import (
    PaperAccount,
    PaperAccountStatus,
    PaperControlAction,
    PaperControlDecision,
)
from osca.paper.persistence import SQLitePaperEvaluationStore
from osca.paper.services import decide_paper_control, evaluate_paper_health_gate


class PaperEvaluationDesktopService(paper_forward.PaperForwardDesktopService):
    """D9 desktop authority with retained M8 account/control identities."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._handlers.update(
            {
                "paper.account.list": self._account_list,
                "paper.account.create": self._account_create,
                "paper.account.control.record": self._account_control_record,
                "paper.run.bind": self._run_bind,
                "paper.run.inspect": self._run_inspect,
                "paper.order.confirm": self._order_confirm,
                "paper.order.process_bar": self._order_process_bar,
            }
        )

    def _account_list(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(params, {"profile_root"}, "paper.account.list")
        profile_root = paper_forward._required_path(params, "profile_root")
        store = _evaluation_store(profile_root)
        accounts = _evaluation_call(store.list_paper_accounts)
        records: list[dict[str, Any]] = []
        for account in accounts:
            controls = _list_control_decisions(store, account.paper_account_id)
            records.append(
                {
                    "account": account.model_dump(mode="json"),
                    "latest_control": (
                        controls[-1].model_dump(mode="json") if controls else None
                    ),
                }
            )
        return paper_forward._safe_result(
            "osca.desktop-paper-account-list.result",
            accounts=records,
        )

    def _account_create(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "name", "base_currency", "created_at"},
            "paper.account.create",
        )
        profile_root = paper_forward._required_path(params, "profile_root")
        account = paper_forward._model_call(
            lambda: PaperAccount(
                name=paper_forward._required_text(params, "name", limit=128),
                base_currency=paper_forward._required_text(
                    params,
                    "base_currency",
                    limit=3,
                ).upper(),
                created_at=paper_forward._optional_datetime(params, "created_at")
                or datetime.now().astimezone(),
            )
        )
        store = _evaluation_store(profile_root)
        with ProfileMutationLock(profile_root):
            _evaluation_call(lambda: store.save_paper_account(account))
        return paper_forward._safe_result(
            "osca.desktop-paper-account-create.result",
            account=account,
        )

    def _account_control_record(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {"profile_root", "paper_account_id", "action", "reason"},
            "paper.account.control.record",
        )
        profile_root = paper_forward._required_path(params, "profile_root")
        account_id = paper_forward._required_uuid(params, "paper_account_id")
        try:
            action = PaperControlAction(
                paper_forward._required_text(params, "action", limit=32)
            )
        except ValueError as exc:
            raise DesktopServiceError("invalid_parameters", "action is invalid") from exc
        reason = paper_forward._required_text(params, "reason", limit=500)
        store = _evaluation_store(profile_root)
        with ProfileMutationLock(profile_root):
            account = _require_account(store, account_id)
            if account.status is PaperAccountStatus.CLOSED:
                raise DesktopServiceError(
                    "paper_account_closed",
                    "closed paper accounts cannot receive new control decisions",
                )
            decision = _decision_for_action(account_id, action, reason)
            _evaluation_call(lambda: store.save_control_decision(decision))
        return paper_forward._safe_result(
            "osca.desktop-paper-account-control.result",
            account=account,
            control_decision=decision,
        )

    def _run_bind(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "paper_run_id",
                "paper_account_id",
                "portfolio_id",
                "approved_candidate_id",
                "created_at",
            },
            "paper.run.bind",
        )
        profile_root = paper_forward._required_path(params, "profile_root")
        account_id = paper_forward._required_uuid(params, "paper_account_id")
        evaluation_store = _evaluation_store(profile_root)
        service = paper_forward._paper_service(profile_root)
        with ProfileMutationLock(profile_root):
            account = _require_active_account(evaluation_store, account_id)
            binding = paper_forward._paper_call(
                lambda: service.bind_run(
                    paper_run_id=paper_forward._required_uuid(params, "paper_run_id"),
                    paper_account_id=account.paper_account_id,
                    portfolio_id=paper_forward._required_uuid(params, "portfolio_id"),
                    approved_candidate_id=_optional_uuid(params, "approved_candidate_id"),
                    created_at=paper_forward._optional_datetime(params, "created_at"),
                )
            )
        return paper_forward._safe_result(
            "osca.desktop-paper-run-bind.result",
            binding=binding,
            paper_account=account,
        )

    def _run_inspect(self, params: dict[str, Any]) -> dict[str, Any]:
        result = super()._run_inspect(params)
        profile_root = paper_forward._required_path(params, "profile_root")
        binding = result.get("binding")
        if not isinstance(binding, dict):
            raise DesktopServiceError("paper_error", "paper run binding is malformed")
        account_id = UUID(str(binding["paper_account_id"]))
        run_id = paper_forward._required_uuid(params, "paper_run_id")
        store = _evaluation_store(profile_root)
        account = _require_account(store, account_id)
        controls = _list_control_decisions(store, account_id)
        health_gates = _evaluation_call(lambda: store.list_health_gates(run_id))
        result["paper_account"] = account.model_dump(mode="json")
        result["control_decisions"] = [item.model_dump(mode="json") for item in controls]
        result["health_gates"] = [item.model_dump(mode="json") for item in health_gates]
        return result

    def _order_confirm(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            {
                "profile_root",
                "paper_run_id",
                "draft_id",
                "draft_version",
                "confirmed_at",
            },
            "paper.order.confirm",
        )
        profile_root = paper_forward._required_path(params, "profile_root")
        run_id = paper_forward._required_uuid(params, "paper_run_id")
        draft_id = paper_forward._required_uuid(params, "draft_id")
        draft_version = paper_forward._optional_int(
            params,
            "draft_version",
            1,
            minimum=1,
        )
        service = paper_forward._paper_service(profile_root)
        store = _evaluation_store(profile_root)
        drafts = paper_forward._paper_call(lambda: service.store.list_drafts(run_id))
        draft = next(
            (
                item
                for item in drafts
                if item.draft_id == draft_id and item.draft_version == draft_version
            ),
            None,
        )
        if draft is None:
            raise DesktopServiceError(
                "paper_not_found",
                "retained simulated-order draft was not found",
            )
        with ProfileMutationLock(profile_root):
            _require_account(store, draft.paper_account_id)
            control = _effective_control(store, draft.paper_account_id)
            result = paper_forward._paper_call(
                lambda: service.confirm_draft(
                    draft,
                    confirmed_at=paper_forward._required_datetime(
                        params,
                        "confirmed_at",
                    ),
                    control_decision=control,
                )
            )
        return paper_forward._safe_result(
            "osca.desktop-paper-order-confirm.result",
            confirmation=result.confirmation,
            order=result.order,
            risk_decision=result.risk_decision,
            lifecycle=result.lifecycle,
            control_decision=control,
            simulated_only=True,
        )

    def _order_process_bar(self, params: dict[str, Any]) -> dict[str, Any]:
        _allowed(
            params,
            paper_forward._BAR_FIELDS
            | {
                "profile_root",
                "order_id",
                "paper_account_id",
                "paper_run_id",
                "data_status",
                "operational_status",
            },
            "paper.order.process_bar",
        )
        profile_root = paper_forward._required_path(params, "profile_root")
        service = paper_forward._paper_service(profile_root)
        evaluation_store = _evaluation_store(profile_root)
        order_id = paper_forward._required_uuid(params, "order_id")
        run_id = paper_forward._required_uuid(params, "paper_run_id")
        supplied_account_id = paper_forward._required_uuid(params, "paper_account_id")
        market_bar = paper_forward._bar_from_params(params)
        with ProfileMutationLock(profile_root):
            order = paper_forward._paper_call(lambda: service.store.get_order(order_id))
            if order.paper_run_id != run_id:
                raise DesktopServiceError(
                    "paper_identity_mismatch",
                    "order paper run does not match requested paper run",
                )
            if order.paper_account_id != supplied_account_id:
                raise DesktopServiceError(
                    "paper_identity_mismatch",
                    "order paper account does not match requested paper account",
                )
            _require_account(evaluation_store, order.paper_account_id)
            control = _effective_control(evaluation_store, order.paper_account_id)
            health = evaluate_paper_health_gate(
                paper_run_id=run_id,
                data_status=paper_forward._health_status(params, "data_status"),
                operational_status=paper_forward._health_status(
                    params,
                    "operational_status",
                ),
            )
            _evaluation_call(lambda: evaluation_store.save_health_gate(health))
            step = paper_forward._paper_call(
                lambda: service.process_bar(
                    order_id,
                    market_bar,
                    control_decision=control,
                    health_gate=health,
                )
            )
        return paper_forward._safe_result(
            "osca.desktop-paper-forward-step.result",
            step=step,
            control_decision=control,
            health_gate=health,
        )


def _evaluation_store(profile_root: Path) -> SQLitePaperEvaluationStore:
    if not profile_root.is_dir():
        raise DesktopServiceError(
            "profile_not_found",
            f"profile directory does not exist: {profile_root}",
        )
    store = SQLitePaperEvaluationStore(profile_root / "paper.sqlite")
    _evaluation_call(store.initialize)
    return store


def _evaluation_call[T](operation: Callable[[], T]) -> T:
    try:
        return operation()
    except sqlite3.Error as exc:
        raise DesktopServiceError("paper_error", f"paper metadata store failed: {exc}") from exc


def _list_control_decisions(
    store: SQLitePaperEvaluationStore,
    account_id: UUID,
) -> tuple[PaperControlDecision, ...]:
    return _evaluation_call(lambda: store.list_control_decisions(account_id))


def _require_account(store: SQLitePaperEvaluationStore, account_id: UUID) -> PaperAccount:
    accounts = _evaluation_call(store.list_paper_accounts)
    account = next((item for item in accounts if item.paper_account_id == account_id), None)
    if account is None:
        raise DesktopServiceError(
            "paper_account_not_found",
            "retained M8 paper account was not found",
        )
    return account


def _require_active_account(store: SQLitePaperEvaluationStore, account_id: UUID) -> PaperAccount:
    account = _require_account(store, account_id)
    if account.status is not PaperAccountStatus.ACTIVE:
        raise DesktopServiceError(
            "paper_account_inactive",
            "paper account must be active before binding a D9 run; "
            f"status is {account.status.value}",
        )
    return account


def _effective_control(
    store: SQLitePaperEvaluationStore,
    account_id: UUID,
) -> PaperControlDecision:
    account = _require_account(store, account_id)
    controls = _list_control_decisions(store, account_id)
    latest = controls[-1] if controls else None
    if account.status is PaperAccountStatus.CLOSED:
        if latest is not None and latest.action is PaperControlAction.PAUSE:
            return latest
        decision = decide_paper_control(
            paper_account_id=account_id,
            account_paused=True,
            reason="retained paper account is closed",
        )
        _evaluation_call(lambda: store.save_control_decision(decision))
        return decision
    if account.status is PaperAccountStatus.PAUSED:
        if latest is not None and latest.action is PaperControlAction.PAUSE:
            return latest
        decision = decide_paper_control(
            paper_account_id=account_id,
            account_paused=True,
            reason="retained paper account is paused",
        )
        _evaluation_call(lambda: store.save_control_decision(decision))
        return decision
    if latest is not None:
        return latest
    decision = decide_paper_control(
        paper_account_id=account_id,
        reason="retained active paper account allows local simulation",
    )
    _evaluation_call(lambda: store.save_control_decision(decision))
    return decision


def _decision_for_action(
    account_id: UUID,
    action: PaperControlAction,
    reason: str,
) -> PaperControlDecision:
    if action is PaperControlAction.KILL_SWITCH:
        return decide_paper_control(
            paper_account_id=account_id,
            kill_switch_engaged=True,
            reason=reason,
        )
    if action is PaperControlAction.PAUSE:
        return decide_paper_control(
            paper_account_id=account_id,
            account_paused=True,
            reason=reason,
        )
    return decide_paper_control(paper_account_id=account_id, reason=reason)


def _optional_uuid(params: dict[str, Any], name: str) -> UUID | None:
    if name not in params or params[name] is None:
        return None
    return paper_forward._required_uuid(params, name)
