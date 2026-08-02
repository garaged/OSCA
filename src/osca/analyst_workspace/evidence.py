from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse

from osca.analyst_workspace.contracts import (
    AnalystWorkspaceSnapshot,
    WorkspaceArtifactDetail,
    WorkspaceExportManifest,
    WorkspaceFilter,
    WorkspaceItem,
    WorkspaceItemStatus,
    WorkspaceLineageLink,
    WorkspaceSection,
)
from osca.analyst_workspace.services import AnalystWorkspaceService

_ID_KEYS = {
    "dataset_revision_id",
    "acquisition_id",
    "experiment_id",
    "diagnostic_id",
    "validation_id",
    "run_id",
    "request_id",
    "correlation_id",
    "job_id",
}
_TIME_KEYS = (
    "completed_at",
    "generated_at",
    "created_at",
    "started_at",
    "requested_at",
)
_EXPECTED_FAMILIES = {
    WorkspaceSection.ACQUISITIONS: "osca.historical-acquisition.",
    WorkspaceSection.EXPERIMENTS: "osca.ml-experiment.",
    WorkspaceSection.DIAGNOSTICS: "osca.prediction-diagnostic.",
    WorkspaceSection.VALIDATIONS: "osca.model-research-validation.",
    WorkspaceSection.PIPELINE_RUNS: "osca.research-pipeline.",
}
_REQUIRED_PARENT = {
    WorkspaceSection.EXPERIMENTS: "dataset_revision_id",
    WorkspaceSection.DIAGNOSTICS: "experiment_id",
    WorkspaceSection.VALIDATIONS: "diagnostic_id",
    WorkspaceSection.PIPELINE_RUNS: "experiment_id",
}


class WorkspaceEvidenceService:
    def __init__(self, workspace: AnalystWorkspaceService | None = None) -> None:
        self._workspace = workspace or AnalystWorkspaceService()

    def filtered_snapshot(
        self,
        storage_root: Path,
        filters: WorkspaceFilter,
    ) -> AnalystWorkspaceSnapshot:
        snapshot = _reconcile(self._workspace.snapshot(storage_root))
        sections = []
        for section in snapshot.sections:
            if filters.section is not None and section.section is not filters.section:
                continue
            items = tuple(item for item in section.items if _matches(item, filters))
            sections.append(section.model_copy(update={"items": items, "item_count": len(items)}))
        return snapshot.model_copy(
            update={
                "sections": tuple(sections),
                "total_items": sum(section.item_count for section in sections),
            }
        )

    def detail(self, storage_root: Path, item_id: str) -> WorkspaceArtifactDetail:
        root = storage_root.resolve()
        snapshot = _reconcile(self._workspace.snapshot(root))
        item = _find_item(snapshot, item_id)
        if item is None:
            raise KeyError(item_id)
        warnings: list[str] = []
        document = _read_item_document(root, item, warnings)
        lineage = _lineage(snapshot, item, document)
        raw_enabled = document is not None and _item_path(root, item) is not None
        portable_enabled = raw_enabled and _portable_allowed(item, document)
        return WorkspaceArtifactDetail(
            item=item,
            document=document,
            lineage=lineage,
            warnings=tuple(warnings),
            raw_json_download_enabled=raw_enabled,
            portable_export_enabled=portable_enabled,
        )

    def raw_json(self, storage_root: Path, item_id: str) -> tuple[str, bytes]:
        detail = self.detail(storage_root, item_id)
        path = _item_path(storage_root.resolve(), detail.item)
        if path is None or path.suffix.lower() != ".json":
            raise ValueError("artifact is not a retained JSON file")
        return path.name, path.read_bytes()

    def portable_export(self, storage_root: Path, item_id: str) -> bytes:
        root = storage_root.resolve()
        snapshot = _reconcile(self._workspace.snapshot(root))
        detail = self.detail(root, item_id)
        candidates = [detail.item]
        for link in detail.lineage:
            linked = _find_item(snapshot, link.item_id)
            if linked is not None:
                candidates.append(linked)

        included: list[WorkspaceItem] = []
        excluded: list[WorkspaceItem] = []
        seen: set[str] = set()
        for item in candidates:
            if item.item_id in seen:
                continue
            seen.add(item.item_id)
            document = _read_item_document(root, item, [])
            if document is not None and _portable_allowed(item, document):
                included.append(item)
            else:
                excluded.append(item)

        if not included:
            raise ValueError("provider policy does not permit portable export")

        manifest = WorkspaceExportManifest(
            root_item_id=item_id,
            included_item_ids=tuple(item.item_id for item in included),
            excluded_item_ids=tuple(item.item_id for item in excluded),
            findings=(
                "portable-local-evidence-only",
                "provider-restricted-or-non-json-artifacts-excluded",
            ),
        )
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("manifest.json", manifest.model_dump_json(indent=2))
            for index, item in enumerate(included, start=1):
                path = _item_path(root, item)
                if path is not None:
                    archive.writestr(f"evidence/{index:02d}-{path.name}", path.read_bytes())
        return output.getvalue()


def _reconcile(snapshot: AnalystWorkspaceSnapshot) -> AnalystWorkspaceSnapshot:
    all_items = [item for section in snapshot.sections for item in section.items]
    known_ids = set().union(*(_identifiers(item.metadata) for item in all_items))
    sections = []
    warnings = list(snapshot.warnings)
    for section in snapshot.sections:
        reconciled = []
        for item in section.items:
            status = item.status
            if item.section in _EXPECTED_FAMILIES:
                family = item.metadata.get("family")
                version = item.metadata.get("version")
                expected = _EXPECTED_FAMILIES[item.section]
                if not isinstance(family, str):
                    status = WorkspaceItemStatus.INCOMPLETE
                    warnings.append(f"Evidence is missing family: {item.item_id}")
                elif not family.startswith(expected):
                    status = WorkspaceItemStatus.INCOMPATIBLE
                    warnings.append(f"Evidence family is incompatible: {item.item_id}")
                elif version is not None and (
                    not isinstance(version, str) or version.split(".", 1)[0] not in {"1", "2"}
                ):
                    status = WorkspaceItemStatus.INCOMPATIBLE
                    warnings.append(f"Evidence version is incompatible: {item.item_id}")
                parent_key = _REQUIRED_PARENT.get(item.section)
                parent = item.metadata.get(parent_key) if parent_key else None
                if parent_key and parent is None:
                    status = WorkspaceItemStatus.INCOMPLETE
                    warnings.append(f"Evidence is missing {parent_key}: {item.item_id}")
                elif parent_key and str(parent) not in known_ids:
                    status = WorkspaceItemStatus.ORPHANED
                    warnings.append(f"Evidence parent is not retained: {item.item_id}")
            reconciled.append(item.model_copy(update={"status": status}))
        sections.append(
            section.model_copy(update={"items": tuple(reconciled), "item_count": len(reconciled)})
        )
    return snapshot.model_copy(update={"sections": tuple(sections), "warnings": tuple(warnings)})


def _find_item(snapshot: AnalystWorkspaceSnapshot, item_id: str) -> WorkspaceItem | None:
    return next(
        (
            item
            for section in snapshot.sections
            for item in section.items
            if item.item_id == item_id
        ),
        None,
    )


def _matches(item: WorkspaceItem, filters: WorkspaceFilter) -> bool:
    if filters.status is not None and item.status is not filters.status:
        return False
    metadata = item.metadata
    if filters.symbol is not None and str(metadata.get("symbol", "")) != filters.symbol:
        return False
    if filters.timeframe is not None and str(metadata.get("timeframe", "")) != filters.timeframe:
        return False
    observed = _item_time(metadata)
    if filters.date_from is not None and (observed is None or observed < filters.date_from):
        return False
    if filters.date_to is not None and (observed is None or observed >= filters.date_to):
        return False
    return True


def _item_time(metadata: dict[str, object]) -> datetime | None:
    for key in _TIME_KEYS:
        raw = metadata.get(key)
        if isinstance(raw, str):
            try:
                return datetime.fromisoformat(raw.replace("Z", "+00:00"))
            except ValueError:
                continue
    return None


def _read_item_document(
    root: Path,
    item: WorkspaceItem,
    warnings: list[str],
) -> dict[str, object] | None:
    path = _item_path(root, item)
    if path is None or path.suffix.lower() != ".json":
        return None
    try:
        decoded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        warnings.append(f"Could not read artifact: {exc}")
        return None
    if not isinstance(decoded, dict):
        warnings.append("Artifact JSON is not an object.")
        return None
    return decoded


def _item_path(root: Path, item: WorkspaceItem) -> Path | None:
    if item.artifact_uri is None:
        return None
    parsed = urlparse(item.artifact_uri)
    candidate = Path(unquote(parsed.path)) if parsed.scheme == "file" else Path(item.artifact_uri)
    path = candidate.resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path if path.is_file() else None


def _lineage(
    snapshot: AnalystWorkspaceSnapshot,
    item: WorkspaceItem,
    document: dict[str, object] | None,
) -> tuple[WorkspaceLineageLink, ...]:
    identity = _identifiers(item.metadata)
    if document is not None:
        identity.update(_identifiers(document))
    links: list[WorkspaceLineageLink] = []
    for candidate in (entry for section in snapshot.sections for entry in section.items):
        if candidate.item_id == item.item_id:
            continue
        if not identity.intersection(_identifiers(candidate.metadata)):
            continue
        links.append(
            WorkspaceLineageLink(
                relation=_relation(item.section, candidate.section),
                item_id=candidate.item_id,
                section=candidate.section,
                title=candidate.title,
                status=candidate.status,
            )
        )
    return tuple(sorted(links, key=lambda link: (link.relation, link.section, link.item_id)))


def _identifiers(document: dict[str, object]) -> set[str]:
    identifiers: set[str] = set()
    for key, value in document.items():
        if key in _ID_KEYS and value is not None:
            identifiers.add(str(value))
        elif key.endswith("_uri") and isinstance(value, str):
            identifiers.add(value)
    return identifiers


def _relation(source: WorkspaceSection, target: WorkspaceSection) -> str:
    order = {
        WorkspaceSection.DATASETS: 0,
        WorkspaceSection.ACQUISITIONS: 1,
        WorkspaceSection.EXPERIMENTS: 2,
        WorkspaceSection.DIAGNOSTICS: 3,
        WorkspaceSection.VALIDATIONS: 4,
        WorkspaceSection.PIPELINE_RUNS: 5,
    }
    source_rank = order.get(source)
    target_rank = order.get(target)
    if source_rank is None or target_rank is None:
        return "related"
    if target_rank < source_rank:
        return "upstream"
    if target_rank > source_rank:
        return "downstream"
    return "related"


def _portable_allowed(item: WorkspaceItem, document: dict[str, object]) -> bool:
    if item.section is WorkspaceSection.ACQUISITIONS:
        if document.get("redistribution_enabled") is not True:
            return False
    return not any(
        key.lower() in {"secret", "token", "password", "api_key", "credential"}
        for key in document
    )
