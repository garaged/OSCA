from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.paper import (
    DeliveryAdapterDeclaration,
    DeliveryAttemptStatus,
    PaperDeliveryAttempt,
    PaperNotificationSeverity,
    build_notification_digest,
    build_paper_notification,
    plan_delivery_attempt,
)


def test_delivery_adapter_cannot_enable_before_configuration() -> None:
    with pytest.raises(ValidationError, match="configuration"):
        DeliveryAdapterDeclaration(
            adapter_id="email.local",
            adapter_kind="email",
            configured=False,
            enabled=True,
        )


def test_failed_delivery_attempt_requires_error_message() -> None:
    with pytest.raises(ValidationError, match="error_message"):
        PaperDeliveryAttempt(
            digest_id=uuid4(),
            adapter_id="email.local",
            status=DeliveryAttemptStatus.FAILED,
        )


def test_notification_digest_preserves_notification_identity() -> None:
    notification = build_paper_notification(
        paper_run_id=uuid4(),
        severity=PaperNotificationSeverity.WARNING,
        title="health-degraded",
        message="paper data health is degraded",
    )
    digest = build_notification_digest(
        paper_run_id=notification.paper_run_id,
        notification_ids=(notification.notification_id,),
    )

    assert digest.paper_run_id == notification.paper_run_id
    assert digest.notification_ids == (notification.notification_id,)


def test_delivery_attempt_skips_disabled_adapter() -> None:
    attempt = plan_delivery_attempt(
        digest_id=uuid4(),
        adapter_id="email.local",
        adapter_enabled=False,
    )

    assert attempt.status is DeliveryAttemptStatus.SKIPPED
