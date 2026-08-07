"""Canonical offline asset catalog and profile-scoped watchlist persistence for D4."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from osca.desktop_api.service import DesktopServiceError


@dataclass(frozen=True, slots=True)
class Asset:
    asset_id: str
    asset_class: str
    symbol: str
    name: str
    venue: str
    currency: str
    aliases: tuple[str, ...] = ()

    def payload(self, profile_root: Path | None = None) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_class": self.asset_class,
            "symbol": self.symbol,
            "name": self.name,
            "venue": self.venue,
            "currency": self.currency,
            "aliases": list(self.aliases),
            "provenance": "bundled-canonical-d4-v1",
            "availability": _availability(profile_root, self),
        }


ASSETS: tuple[Asset, ...] = (
    Asset("equity:XNAS:AAPL", "equity", "AAPL", "Apple Inc.", "XNAS", "USD", ("APPLE",)),
    Asset("equity:XNAS:MSFT", "equity", "MSFT", "Microsoft Corporation", "XNAS", "USD", ("MICROSOFT",)),
    Asset("equity:XNAS:NVDA", "equity", "NVDA", "NVIDIA Corporation", "XNAS", "USD", ("NVIDIA",)),
    Asset("equity:XNYS:ORCL", "equity", "ORCL", "Oracle Corporation", "XNYS", "USD", ("ORACLE",)),
    Asset("equity:ARCX:SPY", "fund", "SPY", "SPDR S&P 500 ETF Trust", "ARCX", "USD", ("S&P 500 ETF",)),
    Asset("crypto:KRAKEN:XBTUSD", "crypto", "XBTUSD", "Bitcoin / US Dollar", "KRAKEN", "USD", ("BTCUSD", "BTC", "XBT")),
    Asset("crypto:KRAKEN:ETHUSD", "crypto", "ETHUSD", "Ether / US Dollar", "KRAKEN", "USD", ("ETH", "ETHEREUM")),
    Asset("crypto:KRAKEN:SOLUSD", "crypto", "SOLUSD", "Solana / US Dollar", "KRAKEN", "USD", ("SOL", "SOLANA")),
    Asset("equity:XNAS:ABC", "equity", "ABC", "Alpha Beta Corporation", "XNAS", "USD"),
    Asset("equity:XNYS:ABC", "equity", "ABC", "Amerisource Bergen Example", "XNYS", "USD"),
)

ASSET_BY_ID = {asset.asset_id: asset for asset in ASSETS}


def search_assets(
    query: str = "",
    *,
    asset_class: str | None = None,
    venue: str | None = None,
    limit: int = 50,
    offset: int = 0,
    profile_root: Path | None = None,
) -> dict[str, Any]:
    normalized = query.strip().upper()
    if limit < 1 or limit > 200 or offset < 0:
        raise DesktopServiceError("invalid_parameters", "limit must be 1..200 and offset non-negative")

    ranked: list[tuple[int, str, Asset]] = []
    for asset in ASSETS:
        if asset_class and asset.asset_class != asset_class:
            continue
        if venue and asset.venue != venue.upper():
            continue
        score = _score(asset, normalized)
        if normalized and score == 0:
            continue
        ranked.append((score, asset.asset_id, asset))
    ranked.sort(key=lambda row: (-row[0], row[1]))
    selected = [asset.payload(profile_root) for _, _, asset in ranked[offset : offset + limit]]
    exact = [asset for _, _, asset in ranked if normalized and _is_exact(asset, normalized)]
    return {
        "family": "osca.desktop-asset-search.result",
        "version": "1.0.0",
        "query": query,
        "total": len(ranked),
        "offset": offset,
        "limit": limit,
        "ambiguous": len(exact) > 1,
        "exact_match_count": len(exact),
        "assets": selected,
        "network_access_enabled": False,
    }


def get_asset(asset_id: str, profile_root: Path | None = None) -> dict[str, Any]:
    asset = ASSET_BY_ID.get(asset_id)
    if asset is None:
        raise DesktopServiceError("asset_not_found", f"Unknown canonical asset: {asset_id}")
    return {
        "family": "osca.desktop-asset-detail.result",
        "version": "1.0.0",
        "asset": asset.payload(profile_root),
        "provider_aliases": [
            {"provider_id": "kraken", "symbol": asset.symbol, "canonical": asset.asset_id}
        ] if asset.venue == "KRAKEN" else [],
        "recommendations_enabled": False,
        "live_execution_enabled": False,
    }


def list_watchlists(profile_root: Path) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        rows = connection.execute(
            "SELECT id, name, created_at, updated_at FROM watchlists ORDER BY lower(name), id"
        ).fetchall()
        watchlists = [_watchlist_payload(connection, row) for row in rows]
    return {"family": "osca.desktop-watchlist-list.result", "version": "1.0.0", "watchlists": watchlists}


def create_watchlist(profile_root: Path, name: str) -> dict[str, Any]:
    normalized = _watchlist_name(name)
    with _connect(profile_root) as connection:
        try:
            cursor = connection.execute(
                "INSERT INTO watchlists(name) VALUES (?)", (normalized,)
            )
        except sqlite3.IntegrityError as exc:
            raise DesktopServiceError("watchlist_conflict", "A watchlist with that name already exists") from exc
        row = connection.execute(
            "SELECT id, name, created_at, updated_at FROM watchlists WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        assert row is not None
        payload = _watchlist_payload(connection, row)
    return {"family": "osca.desktop-watchlist.result", "version": "1.0.0", "watchlist": payload}


def rename_watchlist(profile_root: Path, watchlist_id: int, name: str) -> dict[str, Any]:
    normalized = _watchlist_name(name)
    with _connect(profile_root) as connection:
        try:
            cursor = connection.execute(
                "UPDATE watchlists SET name=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (normalized, watchlist_id),
            )
        except sqlite3.IntegrityError as exc:
            raise DesktopServiceError("watchlist_conflict", "A watchlist with that name already exists") from exc
        if cursor.rowcount != 1:
            raise DesktopServiceError("watchlist_not_found", "Watchlist was not found")
        row = connection.execute(
            "SELECT id, name, created_at, updated_at FROM watchlists WHERE id=?", (watchlist_id,)
        ).fetchone()
        assert row is not None
        payload = _watchlist_payload(connection, row)
    return {"family": "osca.desktop-watchlist.result", "version": "1.0.0", "watchlist": payload}


def delete_watchlist(profile_root: Path, watchlist_id: int) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        cursor = connection.execute("DELETE FROM watchlists WHERE id=?", (watchlist_id,))
        if cursor.rowcount != 1:
            raise DesktopServiceError("watchlist_not_found", "Watchlist was not found")
    return {"family": "osca.desktop-watchlist-delete.result", "version": "1.0.0", "deleted": True, "watchlist_id": watchlist_id}


def add_watchlist_asset(profile_root: Path, watchlist_id: int, asset_id: str) -> dict[str, Any]:
    _require_asset(asset_id)
    with _connect(profile_root) as connection:
        _require_watchlist(connection, watchlist_id)
        next_position = connection.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM watchlist_assets WHERE watchlist_id=?",
            (watchlist_id,),
        ).fetchone()[0]
        connection.execute(
            "INSERT OR IGNORE INTO watchlist_assets(watchlist_id, asset_id, position) VALUES (?, ?, ?)",
            (watchlist_id, asset_id, next_position),
        )
        row = connection.execute(
            "SELECT id, name, created_at, updated_at FROM watchlists WHERE id=?", (watchlist_id,)
        ).fetchone()
        assert row is not None
        payload = _watchlist_payload(connection, row)
    return {"family": "osca.desktop-watchlist.result", "version": "1.0.0", "watchlist": payload}


def remove_watchlist_asset(profile_root: Path, watchlist_id: int, asset_id: str) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        _require_watchlist(connection, watchlist_id)
        connection.execute(
            "DELETE FROM watchlist_assets WHERE watchlist_id=? AND asset_id=?", (watchlist_id, asset_id)
        )
        _resequence(connection, watchlist_id)
        row = connection.execute(
            "SELECT id, name, created_at, updated_at FROM watchlists WHERE id=?", (watchlist_id,)
        ).fetchone()
        assert row is not None
        payload = _watchlist_payload(connection, row)
    return {"family": "osca.desktop-watchlist.result", "version": "1.0.0", "watchlist": payload}


def reorder_watchlist(profile_root: Path, watchlist_id: int, asset_ids: list[str]) -> dict[str, Any]:
    if len(asset_ids) != len(set(asset_ids)):
        raise DesktopServiceError("invalid_parameters", "asset_ids cannot contain duplicates")
    for asset_id in asset_ids:
        _require_asset(asset_id)
    with _connect(profile_root) as connection:
        _require_watchlist(connection, watchlist_id)
        current = [row[0] for row in connection.execute(
            "SELECT asset_id FROM watchlist_assets WHERE watchlist_id=? ORDER BY position", (watchlist_id,)
        )]
        if set(current) != set(asset_ids):
            raise DesktopServiceError("watchlist_membership_mismatch", "Reorder must contain every current member exactly once")
        for position, asset_id in enumerate(asset_ids):
            connection.execute(
                "UPDATE watchlist_assets SET position=? WHERE watchlist_id=? AND asset_id=?",
                (position, watchlist_id, asset_id),
            )
        row = connection.execute(
            "SELECT id, name, created_at, updated_at FROM watchlists WHERE id=?", (watchlist_id,)
        ).fetchone()
        assert row is not None
        payload = _watchlist_payload(connection, row)
    return {"family": "osca.desktop-watchlist.result", "version": "1.0.0", "watchlist": payload}


def record_recent(profile_root: Path, asset_id: str) -> dict[str, Any]:
    _require_asset(asset_id)
    with _connect(profile_root) as connection:
        connection.execute(
            "INSERT INTO recent_assets(asset_id, viewed_at) VALUES (?, CURRENT_TIMESTAMP) "
            "ON CONFLICT(asset_id) DO UPDATE SET viewed_at=CURRENT_TIMESTAMP",
            (asset_id,),
        )
    return list_recent(profile_root)


def list_recent(profile_root: Path, limit: int = 10) -> dict[str, Any]:
    if limit < 1 or limit > 50:
        raise DesktopServiceError("invalid_parameters", "limit must be 1..50")
    with _connect(profile_root) as connection:
        ids = [row[0] for row in connection.execute(
            "SELECT asset_id FROM recent_assets ORDER BY viewed_at DESC, asset_id LIMIT ?", (limit,)
        )]
    return {"family": "osca.desktop-recent-assets.result", "version": "1.0.0", "assets": [ASSET_BY_ID[item].payload(profile_root) for item in ids]}


def _score(asset: Asset, query: str) -> int:
    if not query:
        return 1
    if asset.asset_id.upper() == query:
        return 100
    if asset.symbol.upper() == query:
        return 90
    if query in (alias.upper() for alias in asset.aliases):
        return 85
    if asset.symbol.upper().startswith(query):
        return 70
    if asset.name.upper().startswith(query):
        return 60
    haystack = " ".join((asset.asset_id, asset.symbol, asset.name, asset.venue, *asset.aliases)).upper()
    return 40 if query in haystack else 0


def _is_exact(asset: Asset, query: str) -> bool:
    return query in {asset.asset_id.upper(), asset.symbol.upper(), *(alias.upper() for alias in asset.aliases)}


def _require_asset(asset_id: str) -> Asset:
    asset = ASSET_BY_ID.get(asset_id)
    if asset is None:
        raise DesktopServiceError("asset_not_found", f"Unknown canonical asset: {asset_id}")
    return asset


def _watchlist_name(name: str) -> str:
    normalized = name.strip()
    if not normalized or len(normalized) > 80:
        raise DesktopServiceError("invalid_parameters", "Watchlist name must contain 1..80 characters")
    return normalized


def _profile_database(profile_root: Path) -> Path:
    if not profile_root.is_absolute() or not profile_root.is_dir():
        raise DesktopServiceError("profile_unavailable", "A valid absolute profile directory is required")
    directory = profile_root / ".osca" / "desktop"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "d4-assets.sqlite3"


def _connect(profile_root: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(_profile_database(profile_root))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS watchlists(
          id INTEGER PRIMARY KEY,
          name TEXT NOT NULL COLLATE NOCASE UNIQUE,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS watchlist_assets(
          watchlist_id INTEGER NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
          asset_id TEXT NOT NULL,
          position INTEGER NOT NULL,
          PRIMARY KEY(watchlist_id, asset_id),
          UNIQUE(watchlist_id, position)
        );
        CREATE TABLE IF NOT EXISTS recent_assets(
          asset_id TEXT PRIMARY KEY,
          viewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        PRAGMA user_version=1;
        """
    )
    return connection


def _require_watchlist(connection: sqlite3.Connection, watchlist_id: int) -> None:
    if connection.execute("SELECT 1 FROM watchlists WHERE id=?", (watchlist_id,)).fetchone() is None:
        raise DesktopServiceError("watchlist_not_found", "Watchlist was not found")


def _watchlist_payload(connection: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    members = [
        ASSET_BY_ID[item[0]].payload()
        for item in connection.execute(
            "SELECT asset_id FROM watchlist_assets WHERE watchlist_id=? ORDER BY position, asset_id",
            (row["id"],),
        )
        if item[0] in ASSET_BY_ID
    ]
    return {"watchlist_id": row["id"], "name": row["name"], "created_at": row["created_at"], "updated_at": row["updated_at"], "assets": members}


def _resequence(connection: sqlite3.Connection, watchlist_id: int) -> None:
    ids = [row[0] for row in connection.execute(
        "SELECT asset_id FROM watchlist_assets WHERE watchlist_id=? ORDER BY position, asset_id", (watchlist_id,)
    )]
    for position, asset_id in enumerate(ids):
        connection.execute(
            "UPDATE watchlist_assets SET position=? WHERE watchlist_id=? AND asset_id=?",
            (position, watchlist_id, asset_id),
        )


def _availability(profile_root: Path | None, asset: Asset) -> dict[str, Any]:
    if profile_root is None or not profile_root.is_dir():
        return {"status": "profile-required", "timeframes": [], "source": None}
    token = asset.symbol.lower()
    matches = []
    try:
        for path in profile_root.rglob("*"):
            if path.is_file() and token in path.name.lower() and path.suffix.lower() in {".parquet", ".csv", ".json"}:
                matches.append(str(path.relative_to(profile_root)))
                if len(matches) == 3:
                    break
    except OSError:
        return {"status": "unknown", "timeframes": [], "source": None}
    return {"status": "available" if matches else "unavailable", "timeframes": [], "source": matches[0] if matches else None}
