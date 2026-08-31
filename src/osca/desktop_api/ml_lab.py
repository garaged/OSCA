"""Governed D10 ML datasets, feature catalog, and retained experiments."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

from pydantic import ValidationError

from osca.desktop_api.portfolio_accounting import _allowed, _required_path, _required_text
from osca.desktop_api.profile_lock import ProfileMutationLock
from osca.desktop_api.service import DesktopServiceError
from osca.desktop_api.workbench_data import GovernedDataset, resolve_governed_dataset
from osca.ml_experiments import (
    ExperimentModel,
    ExperimentTask,
    MLExperimentRequest,
    run_experiment,
)

_SCHEMA_VERSION = 1
_MAX_ITERATIONS = 10_000
_FEATURES: tuple[dict[str, Any], ...] = (
    {
        "feature_id": "return.last.v1",
        "version": 1,
        "name": "Last completed-bar return",
        "value_type": "float",
        "lookback_bars": 2,
        "transformation": "close[t] / close[t-1] - 1",
        "point_in_time_safe": True,
        "missing_data_behavior": "fail_closed",
    },
    {
        "feature_id": "return.mean.v1",
        "version": 1,
        "name": "Rolling mean return",
        "value_type": "float",
        "lookback_bars": "configured_feature_window",
        "transformation": "mean of completed-bar returns in the configured trailing window",
        "point_in_time_safe": True,
        "missing_data_behavior": "fail_closed",
    },
    {
        "feature_id": "return.volatility.v1",
        "version": 1,
        "name": "Rolling return volatility",
        "value_type": "float",
        "lookback_bars": "configured_feature_window",
        "transformation": "population standard deviation of trailing completed-bar returns",
        "point_in_time_safe": True,
        "missing_data_behavior": "fail_closed",
    },
)
_FEATURE_IDS = tuple(str(item["feature_id"]) for item in _FEATURES)
_LABEL_TEMPLATES: tuple[dict[str, Any], ...] = (
    {
        "label_id": "forward_return.v1",
        "version": 1,
        "task": "regression",
        "description": "Close-to-close return at the configured future horizon.",
        "leakage_checked": True,
    },
    {
        "label_id": "forward_direction.v1",
        "version": 1,
        "task": "classification",
        "description": "One when the configured future-horizon return is positive, else zero.",
        "leakage_checked": True,
    },
)
_SURVIVORSHIP_POLICY = "single_asset_no_universe_selection"
_CORPORATE_ACTION_POLICY = "governed_dataset_semantics"
_MISSING_DATA_POLICY = "fail_closed"


def list_catalog(params: dict[str, Any]) -> dict[str, Any]:
    _allowed(params, {"profile_root"}, "ml.catalog.list")
    profile_root = _required_path(params, "profile_root")
    with _connect(profile_root) as connection:
        features = [
            _load_json(row[0], "feature definition")
            for row in connection.execute(
                "SELECT definition_json FROM feature_definitions ORDER BY feature_id, version"
            )
        ]
        labels = [
            _load_json(row[0], "label definition")
            for row in connection.execute(
                "SELECT definition_json FROM label_definitions ORDER BY label_id, version"
            )
        ]
    return _safe_result("osca.desktop-ml-catalog.result", features=features, labels=labels)


def create_experiment(params: dict[str, Any]) -> dict[str, Any]:
    _allowed(
        params,
        {
            "profile_root",
            "name",
            "asset_id",
            "timeframe",
            "task",
            "model",
            "horizon",
            "feature_window",
            "train_fraction",
            "validation_fraction",
            "embargo",
            "ridge_alpha",
            "learning_rate",
            "iterations",
            "random_seed",
            "feature_ids",
            "survivorship_policy",
            "corporate_action_policy",
            "missing_data_policy",
        },
        "ml.experiment.create",
    )
    profile_root = _required_path(params, "profile_root")
    name = _bounded_text(params.get("name"), "Experiment name", 100)
    asset_id = _required_text(params, "asset_id")
    timeframe = _required_text(params, "timeframe")
    dataset = resolve_governed_dataset(profile_root, asset_id=asset_id, timeframe=timeframe)
    feature_ids = _feature_ids(params.get("feature_ids", list(_FEATURE_IDS)))
    task = _enum_text(params, "task", {item.value for item in ExperimentTask})
    model = _enum_text(params, "model", {item.value for item in ExperimentModel})
    _require_policy(params, "survivorship_policy", _SURVIVORSHIP_POLICY)
    _require_policy(params, "corporate_action_policy", _CORPORATE_ACTION_POLICY)
    _require_policy(params, "missing_data_policy", _MISSING_DATA_POLICY)
    request_values = _request_values(params)
    try:
        request = MLExperimentRequest(
            dataset_revision_id=dataset.dataset_revision_id,
            payload_path=dataset.payload_path,
            symbol=dataset.symbol,
            timeframe=dataset.timeframe,
            task=ExperimentTask(task),
            model=ExperimentModel(model),
            **request_values,
        )
    except ValidationError as exc:
        raise DesktopServiceError("ml_experiment_invalid", _validation_message(exc)) from exc
    experiment_id = str(uuid4())
    definition = _definition(
        experiment_id=experiment_id,
        name=name,
        asset_id=asset_id,
        dataset=dataset,
        request=request,
        feature_ids=feature_ids,
    )
    with ProfileMutationLock(profile_root), _connect(profile_root) as connection:
        connection.execute(
            "INSERT INTO experiments(experiment_id, name, status, definition_json, "
            "dataset_revision_id, payload_sha256) VALUES (?, ?, 'planned', ?, ?, ?)",
            (
                experiment_id,
                name,
                _json(definition),
                str(dataset.dataset_revision_id),
                _sha256_file(dataset.payload_path),
            ),
        )
        _event(connection, experiment_id, "experiment.planned", {"name": name})
    return _safe_result(
        "osca.desktop-ml-experiment-create.result",
        experiment=get_experiment_record(profile_root, experiment_id),
    )


def execute_experiment(params: dict[str, Any]) -> dict[str, Any]:
    _allowed(params, {"profile_root", "experiment_id"}, "ml.experiment.run")
    profile_root = _required_path(params, "profile_root")
    experiment_id = _uuid_text(params, "experiment_id")
    with ProfileMutationLock(profile_root), _connect(profile_root) as connection:
        row = _require_experiment(connection, experiment_id)
        if str(row["status"]) == "cancelled":
            raise DesktopServiceError("ml_experiment_cancelled", "The experiment was cancelled.")
        if str(row["status"]) not in {"planned", "failed"}:
            raise DesktopServiceError(
                "ml_experiment_state", "Only planned or failed experiments can be run."
            )
        definition = _load_json(str(row["definition_json"]), "experiment definition")
        connection.execute(
            "UPDATE experiments SET status='running', error_code=NULL, error_message=NULL, "
            "cancel_requested=0, "
            "started_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'), "
            "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE experiment_id=?",
            (experiment_id,),
        )
        _event(connection, experiment_id, "experiment.started", {})
    try:
        dataset = resolve_governed_dataset(
            profile_root,
            asset_id=str(definition["asset_id"]),
            timeframe=str(definition["timeframe"]),
        )
        if str(dataset.dataset_revision_id) != str(definition["dataset_revision_id"]):
            raise DesktopServiceError(
                "ml_dataset_revision_changed",
                "The pinned governed dataset revision is no longer the selected revision.",
            )
        expected_digest = str(definition["payload_sha256"])
        if _sha256_file(dataset.payload_path) != expected_digest:
            raise DesktopServiceError(
                "ml_dataset_integrity_failed",
                "The governed dataset payload no longer matches its planned digest.",
            )
        result = run_experiment(_request_from_definition(definition, dataset))
        payload = result.model_dump(mode="json")
        status = result.status.value
        with (
            ProfileMutationLock(profile_root),
            _connect(profile_root, recover_interrupted=False) as connection,
        ):
            current = _require_experiment(connection, experiment_id)
            if bool(current["cancel_requested"]):
                status = "cancelled"
                payload = {}
            connection.execute(
                "UPDATE experiments SET status=?, result_json=?, output_digest=?, "
                "completed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'), "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE experiment_id=?",
                (status, _json(payload), result.output_digest if payload else None, experiment_id),
            )
            _event(connection, experiment_id, f"experiment.{status}", {})
    except (DesktopServiceError, ValidationError, ValueError, OSError) as exc:
        code = exc.code if isinstance(exc, DesktopServiceError) else "ml_experiment_failed"
        message = str(exc)
        with (
            ProfileMutationLock(profile_root),
            _connect(profile_root, recover_interrupted=False) as connection,
        ):
            connection.execute(
                "UPDATE experiments SET status='failed', error_code=?, error_message=?, "
                "completed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'), "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE experiment_id=?",
                (code, message[:2000], experiment_id),
            )
            _event(connection, experiment_id, "experiment.failed", {"code": code})
        raise DesktopServiceError(code, message) from exc
    return _safe_result(
        "osca.desktop-ml-experiment-run.result",
        experiment=get_experiment_record(profile_root, experiment_id),
    )


def list_experiments(params: dict[str, Any]) -> dict[str, Any]:
    _allowed(params, {"profile_root"}, "ml.experiment.list")
    profile_root = _required_path(params, "profile_root")
    with _connect(profile_root) as connection:
        rows = connection.execute(
            "SELECT experiment_id FROM experiments ORDER BY created_at DESC, experiment_id DESC"
        ).fetchall()
    return _safe_result(
        "osca.desktop-ml-experiment-list.result",
        experiments=[get_experiment_record(profile_root, str(row[0])) for row in rows],
    )


def get_experiment(params: dict[str, Any]) -> dict[str, Any]:
    _allowed(params, {"profile_root", "experiment_id"}, "ml.experiment.get")
    profile_root = _required_path(params, "profile_root")
    experiment_id = _uuid_text(params, "experiment_id")
    return _safe_result(
        "osca.desktop-ml-experiment-get.result",
        experiment=get_experiment_record(profile_root, experiment_id),
    )


def cancel_experiment(params: dict[str, Any]) -> dict[str, Any]:
    _allowed(params, {"profile_root", "experiment_id"}, "ml.experiment.cancel")
    profile_root = _required_path(params, "profile_root")
    experiment_id = _uuid_text(params, "experiment_id")
    with ProfileMutationLock(profile_root), _connect(profile_root) as connection:
        row = _require_experiment(connection, experiment_id)
        status = str(row["status"])
        if status == "planned":
            connection.execute(
                "UPDATE experiments SET status='cancelled', cancel_requested=1, "
                "completed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'), "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE experiment_id=?",
                (experiment_id,),
            )
            _event(connection, experiment_id, "experiment.cancelled", {})
        elif status == "running":
            connection.execute(
                "UPDATE experiments SET cancel_requested=1, "
                "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE experiment_id=?",
                (experiment_id,),
            )
            _event(connection, experiment_id, "experiment.cancellation_requested", {})
        elif status != "cancelled":
            raise DesktopServiceError(
                "ml_experiment_state", "A completed or failed experiment cannot be cancelled."
            )
    return _safe_result(
        "osca.desktop-ml-experiment-cancel.result",
        experiment=get_experiment_record(profile_root, experiment_id),
    )


def get_experiment_record(profile_root: Path, experiment_id: str) -> dict[str, Any]:
    with _connect(profile_root) as connection:
        row = _require_experiment(connection, experiment_id)
        events = [
            {
                "event_type": str(item["event_type"]),
                "details": _load_json(str(item["details_json"]), "experiment event"),
                "created_at": str(item["created_at"]),
            }
            for item in connection.execute(
                "SELECT event_type, details_json, created_at FROM experiment_events "
                "WHERE experiment_id=? ORDER BY id",
                (experiment_id,),
            )
        ]
    return {
        "experiment_id": str(row["experiment_id"]),
        "name": str(row["name"]),
        "status": str(row["status"]),
        "definition": _load_json(str(row["definition_json"]), "experiment definition"),
        "result": (
            _load_json(str(row["result_json"]), "experiment result") if row["result_json"] else None
        ),
        "output_digest": str(row["output_digest"]) if row["output_digest"] else None,
        "error": (
            {"code": str(row["error_code"]), "message": str(row["error_message"])}
            if row["error_code"]
            else None
        ),
        "cancel_requested": bool(row["cancel_requested"]),
        "created_at": str(row["created_at"]),
        "started_at": str(row["started_at"]) if row["started_at"] else None,
        "completed_at": str(row["completed_at"]) if row["completed_at"] else None,
        "updated_at": str(row["updated_at"]),
        "events": events,
        "research_only": True,
        "automatic_promotion_enabled": False,
        "recommendations_enabled": False,
        "broker_execution_enabled": False,
        "real_capital_execution_enabled": False,
    }


def _connect(profile_root: Path, *, recover_interrupted: bool = True) -> sqlite3.Connection:
    connection = sqlite3.connect(_database(profile_root))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    current = int(cast(tuple[int], connection.execute("PRAGMA user_version").fetchone())[0])
    if current > _SCHEMA_VERSION:
        connection.close()
        raise DesktopServiceError(
            "ml_schema_newer", "ML Lab data was created by a newer OSCA version."
        )
    if current == 0:
        connection.executescript(
            """
            CREATE TABLE feature_definitions(
              feature_id TEXT NOT NULL,
              version INTEGER NOT NULL,
              definition_json TEXT NOT NULL,
              PRIMARY KEY(feature_id, version)
            );
            CREATE TABLE label_definitions(
              label_id TEXT NOT NULL,
              version INTEGER NOT NULL,
              definition_json TEXT NOT NULL,
              PRIMARY KEY(label_id, version)
            );
            CREATE TABLE experiments(
              experiment_id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              status TEXT NOT NULL CHECK(status IN
                ('planned','running','completed','review_required','failed','cancelled')),
              definition_json TEXT NOT NULL,
              dataset_revision_id TEXT NOT NULL,
              payload_sha256 TEXT NOT NULL,
              result_json TEXT,
              output_digest TEXT,
              error_code TEXT,
              error_message TEXT,
              cancel_requested INTEGER NOT NULL DEFAULT 0 CHECK(cancel_requested IN (0,1)),
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
              started_at TEXT,
              completed_at TEXT,
              updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE experiment_events(
              id INTEGER PRIMARY KEY,
              experiment_id TEXT NOT NULL REFERENCES experiments(experiment_id) ON DELETE CASCADE,
              event_type TEXT NOT NULL,
              details_json TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            PRAGMA user_version=1;
            """
        )
        connection.executemany(
            "INSERT INTO feature_definitions(feature_id, version, definition_json) "
            "VALUES (?, ?, ?)",
            [(item["feature_id"], item["version"], _json(item)) for item in _FEATURES],
        )
        connection.executemany(
            "INSERT INTO label_definitions(label_id, version, definition_json) VALUES (?, ?, ?)",
            [(item["label_id"], item["version"], _json(item)) for item in _LABEL_TEMPLATES],
        )
    if recover_interrupted:
        interrupted = connection.execute(
            "SELECT experiment_id FROM experiments WHERE status='running' ORDER BY experiment_id"
        ).fetchall()
        connection.execute(
            "UPDATE experiments SET status='failed', error_code='ml_experiment_interrupted', "
            "error_message='The desktop process stopped before the retained run completed.', "
            "completed_at=strftime('%Y-%m-%dT%H:%M:%fZ','now'), "
            "updated_at=strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE status='running'"
        )
        for row in interrupted:
            _event(
                connection,
                str(row["experiment_id"]),
                "experiment.failed",
                {"code": "ml_experiment_interrupted"},
            )
    return connection


def _database(profile_root: Path) -> Path:
    if not profile_root.is_absolute() or not profile_root.is_dir():
        raise DesktopServiceError(
            "profile_unavailable", "A valid absolute profile directory is required."
        )
    directory = profile_root / ".osca" / "desktop"
    directory.mkdir(parents=True, exist_ok=True)
    return directory / "d10-ml-lab.sqlite3"


def _definition(
    *,
    experiment_id: str,
    name: str,
    asset_id: str,
    dataset: GovernedDataset,
    request: MLExperimentRequest,
    feature_ids: tuple[str, ...],
) -> dict[str, Any]:
    label = next(item for item in _LABEL_TEMPLATES if item["task"] == request.task.value)
    return {
        "family": "osca.ml-experiment.definition",
        "version": "1.0.0",
        "experiment_id": experiment_id,
        "name": name,
        "asset_id": asset_id,
        "symbol": dataset.symbol,
        "timeframe": dataset.timeframe,
        "dataset_revision_id": str(dataset.dataset_revision_id),
        "payload_sha256": _sha256_file(dataset.payload_path),
        "source_kind": dataset.source_kind,
        "source_attribution": dataset.source_attribution,
        "retained_row_count": dataset.row_count,
        "effective_end": dataset.effective_end.isoformat(),
        "feature_revisions": [item for item in _FEATURES if item["feature_id"] in feature_ids],
        "label_revision": {**label, "horizon_bars": request.horizon},
        "split_policy": {
            "type": "chronological_train_validation_test",
            "train_fraction": request.train_fraction,
            "validation_fraction": request.validation_fraction,
            "purge_bars": request.horizon,
            "embargo_bars": request.embargo,
            "scaler_fit": "training_only",
        },
        "data_policies": {
            "survivorship": _SURVIVORSHIP_POLICY,
            "corporate_actions": _CORPORATE_ACTION_POLICY,
            "missing_data": _MISSING_DATA_POLICY,
        },
        "request": {
            key: value
            for key, value in request.model_dump(mode="json").items()
            if key not in {"payload_path", "dataset_revision_id", "symbol", "timeframe"}
        },
        "resource_budget": {
            "max_source_rows": 50_000,
            "max_iterations": _MAX_ITERATIONS,
            "local_process_only": True,
        },
        "mandatory_baseline": "persistence_or_moving_average",
        "engine_revision": "osca.ml_experiments.engine.v1",
        "code_revision": f"osca-package:{_package_version()}",
    }


def _request_from_definition(
    definition: dict[str, Any], dataset: GovernedDataset
) -> MLExperimentRequest:
    request = definition.get("request")
    if not isinstance(request, dict):
        raise DesktopServiceError("ml_store_corrupt", "Experiment request is malformed.")
    return MLExperimentRequest(
        dataset_revision_id=dataset.dataset_revision_id,
        payload_path=dataset.payload_path,
        symbol=dataset.symbol,
        timeframe=dataset.timeframe,
        **request,
    )


def _request_values(params: dict[str, Any]) -> dict[str, Any]:
    values = {
        key: params[key]
        for key in (
            "horizon",
            "feature_window",
            "train_fraction",
            "validation_fraction",
            "embargo",
            "ridge_alpha",
            "learning_rate",
            "iterations",
            "random_seed",
        )
        if key in params
    }
    if int(values.get("iterations", 500)) > _MAX_ITERATIONS:
        raise DesktopServiceError(
            "ml_resource_budget_exceeded", f"iterations must not exceed {_MAX_ITERATIONS}"
        )
    return values


def _require_experiment(connection: sqlite3.Connection, experiment_id: str) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM experiments WHERE experiment_id=?", (experiment_id,)
    ).fetchone()
    if row is None:
        raise DesktopServiceError("ml_experiment_not_found", "Experiment was not found.")
    return cast(sqlite3.Row, row)


def _event(
    connection: sqlite3.Connection,
    experiment_id: str,
    event_type: str,
    details: dict[str, Any],
) -> None:
    connection.execute(
        "INSERT INTO experiment_events(experiment_id, event_type, details_json) VALUES (?, ?, ?)",
        (experiment_id, event_type, _json(details)),
    )


def _feature_ids(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise DesktopServiceError("ml_experiment_invalid", "Select at least one feature.")
    feature_ids = tuple(str(item) for item in value)
    if len(set(feature_ids)) != len(feature_ids) or any(
        item not in _FEATURE_IDS for item in feature_ids
    ):
        raise DesktopServiceError(
            "ml_experiment_invalid", "Feature selection contains an unknown or duplicate ID."
        )
    if feature_ids != _FEATURE_IDS:
        raise DesktopServiceError(
            "ml_experiment_invalid",
            "The initial bounded trainer requires all three governed return features.",
        )
    return feature_ids


def _enum_text(params: dict[str, Any], field: str, allowed: set[str]) -> str:
    value = _required_text(params, field)
    if value not in allowed:
        raise DesktopServiceError(
            "ml_experiment_invalid", f"{field} must be one of: {', '.join(sorted(allowed))}."
        )
    return value


def _require_policy(params: dict[str, Any], field: str, expected: str) -> None:
    value = params.get(field, expected)
    if value != expected:
        raise DesktopServiceError("ml_experiment_invalid", f"{field} must be {expected}.")


def _uuid_text(params: dict[str, Any], field: str) -> str:
    value = _required_text(params, field)
    try:
        return str(UUID(value))
    except ValueError as exc:
        raise DesktopServiceError("ml_experiment_invalid", f"{field} must be a UUID.") from exc


def _bounded_text(value: Any, field: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DesktopServiceError("ml_experiment_invalid", f"{field} is required.")
    normalized = value.strip()
    if len(normalized) > limit:
        raise DesktopServiceError(
            "ml_experiment_invalid", f"{field} must not exceed {limit} characters."
        )
    return normalized


def _load_json(value: str, field: str) -> dict[str, Any]:
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise DesktopServiceError("ml_store_corrupt", f"{field} is invalid JSON.") from exc
    if not isinstance(decoded, dict):
        raise DesktopServiceError("ml_store_corrupt", f"{field} is malformed.")
    return decoded


def _json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validation_message(exc: ValidationError) -> str:
    return "; ".join(str(item["msg"]) for item in exc.errors())[:2000]


def _package_version() -> str:
    try:
        return version("osca")
    except PackageNotFoundError:
        return "development"


def _safe_result(family: str, **values: Any) -> dict[str, Any]:
    return {
        "family": family,
        "version": "1.0.0",
        **values,
        "research_only": True,
        "network_access_enabled": False,
        "credential_access_enabled": False,
        "automatic_promotion_enabled": False,
        "recommendations_enabled": False,
        "broker_execution_enabled": False,
        "real_capital_execution_enabled": False,
    }
