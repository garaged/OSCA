from osca.llm.contracts import (
    LLMBudget,
    LLMCapability,
    LLMEvaluationReport,
    LLMEvaluationStatus,
    LLMFinding,
    LLMFindingSeverity,
    LLMPrivacyClass,
    LLMProviderCapability,
    LLMRequestEnvelope,
    LLMRouteDecision,
)


def estimate_llm_cost(
    *,
    provider: LLMProviderCapability,
    input_tokens: int,
    output_tokens: int,
) -> float:
    return (
        input_tokens / 1000 * provider.cost_per_1k_input_tokens_usd
        + output_tokens / 1000 * provider.cost_per_1k_output_tokens_usd
    )


def evaluate_llm_route(
    *,
    request: LLMRequestEnvelope,
    providers: tuple[LLMProviderCapability, ...],
    estimated_input_tokens: int,
    estimated_output_tokens: int,
) -> LLMRouteDecision:
    findings: list[LLMFinding] = []
    if estimated_input_tokens > request.budget.max_input_tokens:
        findings.append(
            _error("input_token_budget_exceeded", "estimated input tokens exceed budget")
        )
    if estimated_output_tokens > request.budget.max_output_tokens:
        findings.append(
            _error("output_token_budget_exceeded", "estimated output tokens exceed budget")
        )
    if (
        request.privacy_class is LLMPrivacyClass.SENSITIVE
        and not request.sensitive_disclosure_approved
    ):
        findings.append(
            _error("sensitive_disclosure_blocked", "sensitive disclosure is not approved")
        )

    candidate = _select_provider(
        providers=providers,
        capability=request.requested_capability,
        privacy_class=request.privacy_class,
    )
    if candidate is None:
        findings.append(_error("no_provider_route", "no LLM provider supports the request"))
        return _blocked_route(request=request, findings=tuple(findings))

    estimated_cost = estimate_llm_cost(
        provider=candidate,
        input_tokens=estimated_input_tokens,
        output_tokens=estimated_output_tokens,
    )
    if estimated_cost > request.budget.max_cost_usd:
        findings.append(_error("cost_budget_exceeded", "estimated LLM cost exceeds budget"))

    if findings:
        return _blocked_route(
            request=request,
            findings=tuple(findings),
            estimated_cost=estimated_cost,
        )

    return LLMRouteDecision(
        request_id=request.request_id,
        provider_id=candidate.provider_id,
        model_id=candidate.model_id,
        model_version=candidate.model_version,
        approved=True,
        rationale="LLM route approved by deterministic gateway policy",
        estimated_cost_usd=estimated_cost,
    )


def build_llm_evaluation_report(
    *,
    request: LLMRequestEnvelope,
    route: LLMRouteDecision,
    dimensions: tuple[str, ...],
    findings: tuple[LLMFinding, ...] = (),
    cost_usd: float,
    latency_ms: int,
) -> LLMEvaluationReport:
    has_error = any(finding.severity is LLMFindingSeverity.ERROR for finding in findings)
    status = LLMEvaluationStatus.FAILED if has_error else LLMEvaluationStatus.PASSED
    if not route.approved:
        status = LLMEvaluationStatus.FAILED
    return LLMEvaluationReport(
        request_id=request.request_id,
        route_decision_id=route.route_decision_id,
        status=status,
        evaluated_dimensions=dimensions,
        findings=findings,
        cost_usd=cost_usd,
        latency_ms=latency_ms,
    )


def default_llm_budget() -> LLMBudget:
    return LLMBudget(
        max_input_tokens=8000,
        max_output_tokens=2000,
        max_cost_usd=1.00,
        max_latency_ms=30000,
        max_tool_calls=4,
    )


def _select_provider(
    *,
    providers: tuple[LLMProviderCapability, ...],
    capability: LLMCapability,
    privacy_class: LLMPrivacyClass,
) -> LLMProviderCapability | None:
    for provider in providers:
        if (
            provider.available
            and capability in provider.capabilities
            and privacy_class in provider.supported_privacy_classes
        ):
            return provider
    return None


def _blocked_route(
    *,
    request: LLMRequestEnvelope,
    findings: tuple[LLMFinding, ...],
    estimated_cost: float = 0,
) -> LLMRouteDecision:
    return LLMRouteDecision(
        request_id=request.request_id,
        provider_id=None,
        model_id=None,
        model_version=None,
        approved=False,
        rationale="LLM route blocked by deterministic gateway policy",
        estimated_cost_usd=estimated_cost,
        findings=findings,
    )


def _error(code: str, message: str) -> LLMFinding:
    return LLMFinding(code=code, severity=LLMFindingSeverity.ERROR, message=message)
