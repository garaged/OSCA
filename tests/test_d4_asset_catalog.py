import fcntl
from pathlib import Path

from osca.desktop_api.asset_catalog import (
    add_watchlist_asset,
    create_watchlist,
    list_watchlists,
    search_assets,
)
from osca.desktop_api.contracts import DesktopRequest
from osca.desktop_api.d4_service import D4DesktopApplicationService
from osca.desktop_api.profile_lock import ProfileMutationLock, profile_session_lock_path
from osca.desktop_api.watchlist_order import reorder_watchlist


def test_search_is_deterministic_and_reports_symbol_ambiguity() -> None:
    first = search_assets("ABC")
    second = search_assets("ABC")
    assert first == second
    assert first["ambiguous"] is True
    assert [row["asset_id"] for row in first["assets"]] == [
        "equity:XNAS:ABC",
        "equity:XNYS:ABC",
    ]


def test_alias_resolves_to_canonical_asset() -> None:
    result = search_assets("BTC")
    assert result["ambiguous"] is False
    assert result["assets"][0]["asset_id"] == "crypto:KRAKEN:XBTUSD"


def test_watchlists_persist_ordered_canonical_ids(tmp_path: Path) -> None:
    created = create_watchlist(tmp_path, "Core")
    watchlist_id = created["watchlist"]["watchlist_id"]
    add_watchlist_asset(tmp_path, watchlist_id, "equity:XNAS:AAPL")
    add_watchlist_asset(tmp_path, watchlist_id, "crypto:KRAKEN:XBTUSD")
    reordered = reorder_watchlist(
        tmp_path,
        watchlist_id,
        ["crypto:KRAKEN:XBTUSD", "equity:XNAS:AAPL"],
    )
    assert [item["asset_id"] for item in reordered["watchlist"]["assets"]] == [
        "crypto:KRAKEN:XBTUSD",
        "equity:XNAS:AAPL",
    ]
    reloaded = list_watchlists(tmp_path)
    assert reloaded["watchlists"] == [reordered["watchlist"]]


def test_desktop_methods_remain_typed_and_offline(tmp_path: Path) -> None:
    service = D4DesktopApplicationService(state_root=tmp_path / "state")
    response = service.handle(
        DesktopRequest(
            request_id="d4-search",
            method="asset.search",
            params={"query": "AAPL"},
        )
    )
    assert response.status == "ok"
    assert response.result is not None
    assert response.result["network_access_enabled"] is False
    assert response.result["assets"][0]["asset_id"] == "equity:XNAS:AAPL"


def test_supported_python_mutation_fails_while_desktop_session_owns_profile(tmp_path: Path) -> None:
    profile = tmp_path / "profile"
    session_path = profile_session_lock_path(profile)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    with session_path.open("a+", encoding="utf-8") as session_stream:
        fcntl.flock(session_stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        service = D4DesktopApplicationService(state_root=tmp_path / "state")
        response = service.handle(
            DesktopRequest(
                request_id="d4-cli-lock",
                method="watchlist.create",
                params={"profile_root": str(profile), "name": "CLI Lock Test"},
            )
        )
        assert response.status == "error"
        assert response.error is not None
        assert response.error.code == "profile_locked"
        assert "already open" in response.error.message


def test_broker_authorized_sidecar_reuses_desktop_session_lease(
    tmp_path: Path, monkeypatch: object
) -> None:
    profile = (tmp_path / "profile").resolve()
    session_path = profile_session_lock_path(profile)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    with session_path.open("a+", encoding="utf-8") as session_stream:
        fcntl.flock(session_stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        monkeypatch.setenv("OSCA_DESKTOP_OWNED_PROFILE", str(profile))  # type: ignore[attr-defined]
        with ProfileMutationLock(profile):
            pass
