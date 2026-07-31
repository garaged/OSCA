from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast

from osca.analyst_workspace.contracts import (
    AnalystWorkspaceSnapshot,
    WorkspaceItem,
    WorkspaceItemStatus,
    WorkspaceSection,
    WorkspaceSectionResult,
)

_EMPTY_MESSAGES: dict[WorkspaceSection, str] = {
    WorkspaceSection.PROJECTS: "No retained research-project summaries were found.",
    WorkspaceSection.WATCHLISTS: "No local watchlists were found.",
    WorkspaceSection.DATASETS: "No governed local OHLCV datasets were found.",
    WorkspaceSection.REPORTS: "No retained research reports were found.",
    WorkspaceSection.BACKTESTS: "No retained backtest or paper-evaluation reports were found.",
    WorkspaceSection.ENRICHMENT: "No retained SEC enrichment evidence was found.",
    WorkspaceSection.ROUTING: "No retained runtime-routing decisions were found.",
}


class AnalystWorkspaceService:
    def snapshot(self, storage_root: Path) -> AnalystWorkspaceSnapshot:
        root = storage_root.resolve()
        warnings: list[str] = []
        sections = tuple(
            self.section(root, section, warnings=warnings)
            for section in WorkspaceSection
        )
        return AnalystWorkspaceSnapshot(
            storage_root=str(root),
            sections=sections,
            total_items=sum(section.item_count for section in sections),
            warnings=tuple(warnings),
        )

    def section(
        self,
        storage_root: Path,
        section: WorkspaceSection,
        *,
        warnings: list[str] | None = None,
    ) -> WorkspaceSectionResult:
        root = storage_root.resolve()
        warning_sink = warnings if warnings is not None else []
        loaders = {
            WorkspaceSection.PROJECTS: self._projects,
            WorkspaceSection.WATCHLISTS: self._watchlists,
            WorkspaceSection.DATASETS: self._datasets,
            WorkspaceSection.REPORTS: self._reports,
            WorkspaceSection.BACKTESTS: self._backtests,
            WorkspaceSection.ENRICHMENT: self._enrichment,
            WorkspaceSection.ROUTING: self._routing,
        }
        items = loaders[section](root, warning_sink)
        return WorkspaceSectionResult(
            section=section,
            items=items,
            item_count=len(items),
            empty_message=_EMPTY_MESSAGES[section],
        )

    def _projects(self, root: Path, warnings: list[str]) -> tuple[WorkspaceItem, ...]:
        return _json_directory_items(
            root / "projects",
            section=WorkspaceSection.PROJECTS,
            title_keys=("name", "title", "project_id"),
            warnings=warnings,
        )

    def _watchlists(self, root: Path, warnings: list[str]) -> tuple[WorkspaceItem, ...]:
        return _json_directory_items(
            root / "watchlists",
            section=WorkspaceSection.WATCHLISTS,
            title_keys=("name", "title", "watchlist_id"),
            warnings=warnings,
        )

    def _datasets(self, root: Path, warnings: list[str]) -> tuple[WorkspaceItem, ...]:
        database_path = root / "osca-local-data.sqlite"
        if not database_path.is_file():
            return ()
        try:
            with sqlite3.connect(database_path) as connection:
                connection.row_factory = sqlite3.Row
                rows = connection.execute(
                    """
                    SELECT dataset_revision_id, symbol, timeframe, row_count,
                           first_timestamp, last_timestamp, payload_uri,
                           quality_findings_json
                    FROM local_ohlcv_imports
                    ORDER BY last_timestamp DESC
                    """
                ).fetchall()
        except sqlite3.Error as exc:
            warnings.append(f"Could not inspect local dataset metadata: {exc}")
            return ()
        return tuple(_dataset_item(row) for row in rows)

    def _reports(self, root: Path, warnings: list[str]) -> tuple[WorkspaceItem, ...]:
        paths = _artifact_paths(root, suffixes=(".md", ".json"))
        return tuple(
            _file_item(path, WorkspaceSection.REPORTS, root)
            for path in paths
            if "backtest" not in path.name.lower()
            and "paper" not in path.name.lower()
            and not _is_provider_or_routing_metadata(path)
        )

    def _backtests(self, root: Path, warnings: list[str]) -> tuple[WorkspaceItem, ...]:
        del warnings
        paths = _artifact_paths(root, suffixes=(".md", ".json"))
        return tuple(
            _file_item(path, WorkspaceSection.BACKTESTS, root)
            for path in paths
            if "backtest" in path.name.lower() or "paper" in path.name.lower()
        )

    def _enrichment(self, root: Path, warnings: list[str]) -> tuple[WorkspaceItem, ...]:
        metadata_root = root / "provider-preview" / "sec-edgar"
        return _evidence_items(
            metadata_root,
            section=WorkspaceSection.ENRICHMENT,
            warnings=warnings,
        )

    def _routing(self, root: Path, warnings: list[str]) -> tuple[WorkspaceItem, ...]:
        return _evidence_items(
            root / "runtime-routing",
            section=WorkspaceSection.ROUTING,
            warnings=warnings,
        )


def _dataset_item(row: sqlite3.Row) -> WorkspaceItem:
    quality_findings = _json_list(str(row["quality_findings_json"]))
    status = (
        WorkspaceItemStatus.WARNING
        if quality_findings
        else WorkspaceItemStatus.AVAILABLE
    )
    symbol = str(row["symbol"])
    timeframe = str(row["timeframe"])
    revision = str(row["dataset_revision_id"])
    return WorkspaceItem(
        item_id=f"dataset:{revision}",
        section=WorkspaceSection.DATASETS,
        title=f"{symbol} {timeframe}",
        status=status,
        summary=(
            f"{int(row['row_count'])} bars from {row['first_timestamp']} "
            f"through {row['last_timestamp']}."
        ),
        artifact_uri=str(row["payload_uri"]),
        metadata={
            "dataset_revision_id": revision,
            "symbol": symbol,
            "timeframe": timeframe,
            "row_count": int(row["row_count"]),
            "quality_findings": quality_findings,
        },
    )


def _json_directory_items(
    directory: Path,
    *,
    section: WorkspaceSection,
    title_keys: tuple[str, ...],
    warnings: list[str],
) -> tuple[WorkspaceItem, ...]:
    if not directory.is_dir():
        return ()
    items: list[WorkspaceItem] = []
    for path in sorted(directory.glob("*.json")):
        document = _read_json_object(path, warnings)
        if document is None:
            continue
        title = next(
            (
                str(document[key])
                for key in title_keys
                if key in document and document[key] is not None
            ),
            path.stem,
        )
        items.append(
            WorkspaceItem(
                item_id=f"{section.value}:{path.stem}",
                section=section,
                title=title,
                status=WorkspaceItemStatus.AVAILABLE,
                summary=f"Retained local {section.value[:-1]} artifact.",
                artifact_uri=path.resolve().as_uri(),
                metadata=_safe_metadata(document),
            )
        )
    return tuple(items)


def _evidence_items(
    directory: Path,
    *,
    section: WorkspaceSection,
    warnings: list[str],
) -> tuple[WorkspaceItem, ...]:
    if not directory.is_dir():
        return ()
    items: list[WorkspaceItem] = []
    for path in sorted(directory.rglob("*.metadata.json")) + sorted(
        directory.rglob("*.decision.json")
    ):
        document = _read_json_object(path, warnings)
        if document is None:
            continue
        raw_status = str(document.get("status", document.get("outcome", "available")))
        status = _workspace_status(raw_status)
        provider = str(document.get("provider_id", "local"))
        resource = str(document.get("resource_id", path.stem))
        items.append(
            WorkspaceItem(
                item_id=f"{section.value}:{path.relative_to(directory)}",
                section=section,
                title=f"{provider}: {resource}",
                status=status,
                summary=str(document.get("rationale", "Retained evidence record.")),
                artifact_uri=path.resolve().as_uri(),
                metadata=_safe_metadata(document),
            )
        )
    return tuple(items)


def _file_item(path: Path, section: WorkspaceSection, root: Path) -> WorkspaceItem:
    return WorkspaceItem(
        item_id=f"{section.value}:{path.relative_to(root)}",
        section=section,
        title=path.stem.replace("-", " ").replace("_", " ").title(),
        status=WorkspaceItemStatus.AVAILABLE,
        summary=f"Retained {path.suffix.removeprefix('.').upper()} artifact.",
        artifact_uri=path.resolve().as_uri(),
        metadata={"relative_path": str(path.relative_to(root)), "size_bytes": path.stat().st_size},
    )


def _artifact_paths(root: Path, *, suffixes: tuple[str, ...]) -> tuple[Path, ...]:
    if not root.is_dir():
        return ()
    paths: list[Path] = []
    for suffix in suffixes:
        paths.extend(root.rglob(f"*{suffix}"))
    return tuple(
        sorted(
            path
            for path in paths
            if path.is_file()
            and "/projects/" not in path.as_posix()
            and "/watchlists/" not in path.as_posix()
        )
    )


def _is_provider_or_routing_metadata(path: Path) -> bool:
    value = path.as_posix()
    return "/provider-preview/" in value or "/runtime-routing/" in value


def _read_json_object(path: Path, warnings: list[str]) -> dict[str, object] | None:
    try:
        decoded: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        warnings.append(f"Could not inspect {path}: {exc}")
        return None
    if not isinstance(decoded, dict):
        warnings.append(f"Ignored non-object JSON artifact: {path}")
        return None
    return cast(dict[str, object], decoded)


def _safe_metadata(document: dict[str, object]) -> dict[str, object]:
    excluded = {"secret", "token", "password", "api_key", "credential"}
    return {
        key: value
        for key, value in document.items()
        if not any(term in key.lower() for term in excluded)
        and isinstance(value, (str, int, float, bool, list, dict, type(None)))
    }


def _json_list(value: str) -> list[object]:
    try:
        decoded: Any = json.loads(value)
    except json.JSONDecodeError:
        return []
    return cast(list[object], decoded) if isinstance(decoded, list) else []


def _workspace_status(value: str) -> WorkspaceItemStatus:
    normalized = value.lower()
    if normalized in {"policy_blocked", "blocked"}:
        return WorkspaceItemStatus.POLICY_BLOCKED
    if normalized in {"provider_unavailable", "unavailable"}:
        return WorkspaceItemStatus.PROVIDER_UNAVAILABLE
    if normalized in {"warning", "stale", "partial"}:
        return WorkspaceItemStatus.WARNING
    return WorkspaceItemStatus.AVAILABLE
