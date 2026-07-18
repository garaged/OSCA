from osca.market_data.api import RepairRequest, RetrievalRequest
from osca.security.api import AuthorizationContext, Capability
from osca.shared_kernel.api import CorrelationId
from osca.workflow.api import JobRun, SubmitJob
from osca.workflow.application import JobService
from osca.workflow.application.handlers import require_capability


class MarketDataJobService:
    def __init__(self, jobs: JobService) -> None:
        self._jobs = jobs

    def submit_retrieval(
        self,
        authorization: AuthorizationContext,
        correlation_id: CorrelationId,
        request: RetrievalRequest,
    ) -> JobRun:
        require_capability(authorization, Capability.MARKET_DATA_RETRIEVE)
        return self._jobs.submit(
            SubmitJob(
                authorization=authorization,
                correlation_id=correlation_id,
                kind="market-data.retrieve",
                idempotency_key=request.idempotency_key,
                input_family=request.family,
                input_version=request.version,
                input_payload=request.model_dump(mode="json"),
            )
        )

    def submit_repair(
        self,
        authorization: AuthorizationContext,
        correlation_id: CorrelationId,
        request: RepairRequest,
    ) -> JobRun:
        require_capability(authorization, Capability.MARKET_DATA_REPAIR)
        return self._jobs.submit(
            SubmitJob(
                authorization=authorization,
                correlation_id=correlation_id,
                kind="market-data.repair",
                idempotency_key=request.idempotency_key,
                input_family=request.family,
                input_version=request.version,
                input_payload=request.model_dump(mode="json"),
            )
        )
