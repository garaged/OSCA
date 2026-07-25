from datetime import datetime
from uuid import UUID

from osca.market_data.api import (
    DatasetLayer,
    DatasetManifest,
    DateClassification,
    DateFinding,
    ManifestState,
    ResolutionState,
    RetrievalRequest,
    RetrievalResolution,
)


def resolve_retrieval(
    request: RetrievalRequest,
    *,
    manifests: tuple[DatasetManifest, ...],
    findings: tuple[DateFinding, ...],
    now: datetime,
    corrupt_manifest_ids: frozenset[UUID] = frozenset(),
) -> RetrievalResolution:
    """Resolve a request without hiding freshness, coverage, or integrity state."""
    candidates = tuple(
        manifest
        for manifest in manifests
        if manifest.instrument_id == request.instrument_id
        and manifest.interval == request.interval
        and manifest.layer is DatasetLayer.CANONICAL
        and manifest.state is ManifestState.READY
        and manifest.start_date <= request.start_date
        and manifest.end_date_exclusive >= request.end_date_exclusive
    )
    if request.pinned_revision_id is not None:
        candidates = tuple(
            manifest
            for manifest in candidates
            if manifest.manifest_id == request.pinned_revision_id
        )
    if not candidates:
        return _resolution(
            request,
            ResolutionState.UNAVAILABLE,
            "retrieve_and_validate_requested_range",
            findings,
        )

    selected = max(candidates, key=lambda manifest: (manifest.revision, manifest.created_at))
    if selected.manifest_id in corrupt_manifest_ids:
        return _resolution(
            request,
            ResolutionState.CORRUPT,
            "quarantine_revision_and_repair_from_permitted_evidence",
            findings,
            selected,
        )

    blocking = {
        DateClassification.MISSING,
        DateClassification.UNRESOLVED,
        DateClassification.INCOMPLETE,
    }
    relevant = tuple(
        finding
        for finding in findings
        if request.start_date <= finding.effective_date < request.end_date_exclusive
    )
    if request.require_complete and any(
        finding.classification in blocking for finding in relevant
    ):
        return _resolution(
            request,
            ResolutionState.PARTIAL,
            "repair_confirmed_gaps_and_resolve_uncertain_dates",
            relevant,
            selected,
        )

    age_seconds = (now - selected.created_at).total_seconds()
    if age_seconds > request.maximum_age_seconds:
        return _resolution(
            request,
            ResolutionState.STALE,
            "refresh_then_revalidate_requested_range",
            relevant,
            selected,
        )
    return _resolution(
        request,
        ResolutionState.FRESH,
        "use_exact_resolved_revision",
        relevant,
        selected,
    )


def _resolution(
    request: RetrievalRequest,
    state: ResolutionState,
    remediation: str,
    findings: tuple[DateFinding, ...],
    manifest: DatasetManifest | None = None,
) -> RetrievalResolution:
    return RetrievalResolution(
        request_id=request.request_id,
        state=state,
        dataset_id=manifest.dataset_id if manifest else None,
        revision_id=manifest.manifest_id if manifest else None,
        safe_remediation=remediation,
        findings=tuple(finding.finding_id for finding in findings),
    )
