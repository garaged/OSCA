"""Collision-safe ordered watchlist mutations for D4."""

from pathlib import Path
from typing import Any

from osca.desktop_api.asset_catalog import (
    _connect,
    _require_asset,
    _require_watchlist,
    _watchlist_payload,
)
from osca.desktop_api.service import DesktopServiceError


def reorder_watchlist(
    profile_root: Path,
    watchlist_id: int,
    asset_ids: list[str],
) -> dict[str, Any]:
    """Replace membership positions atomically without unique-key collisions."""
    if len(asset_ids) != len(set(asset_ids)):
        raise DesktopServiceError(
            "invalid_parameters",
            "asset_ids cannot contain duplicates",
        )
    for asset_id in asset_ids:
        _require_asset(asset_id)

    with _connect(profile_root) as connection:
        _require_watchlist(connection, watchlist_id)
        current = [
            row[0]
            for row in connection.execute(
                "SELECT asset_id FROM watchlist_assets "
                "WHERE watchlist_id=? ORDER BY position",
                (watchlist_id,),
            )
        ]
        if set(current) != set(asset_ids):
            raise DesktopServiceError(
                "watchlist_membership_mismatch",
                "Reorder must contain every current member exactly once",
            )

        # Move every row into a disjoint temporary range before assigning
        # final positions. This preserves the unique (watchlist, position)
        # invariant throughout the transaction, including simple swaps.
        for temporary, asset_id in enumerate(current, start=1):
            connection.execute(
                "UPDATE watchlist_assets SET position=? "
                "WHERE watchlist_id=? AND asset_id=?",
                (-temporary, watchlist_id, asset_id),
            )
        for position, asset_id in enumerate(asset_ids):
            connection.execute(
                "UPDATE watchlist_assets SET position=? "
                "WHERE watchlist_id=? AND asset_id=?",
                (position, watchlist_id, asset_id),
            )

        row = connection.execute(
            "SELECT id, name, created_at, updated_at "
            "FROM watchlists WHERE id=?",
            (watchlist_id,),
        ).fetchone()
        assert row is not None
        payload = _watchlist_payload(connection, row)

    return {
        "family": "osca.desktop-watchlist.result",
        "version": "1.0.0",
        "watchlist": payload,
    }
