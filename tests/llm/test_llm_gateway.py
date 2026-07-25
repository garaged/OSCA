from osca.llm import (
    LLMCapability,
    LLMFinding,
    LLMFindingSeverity,
    LLMPrivacyClass,
    LLMProviderCapability,
    LLMRequestEnvelope,
    build_llm_evaluation_report,
    default_llm_budget,
    evaluate_llm_route,
)


def test_gateway_approves_exact_provider_model_route() -> None:
    request = LLMRequestEnvelope(
        requested_capability=LLMCapability.SYNTHESIS,
        privacy_class=LLMPrivacyClass.INTERNAL,
        prompt_template_id="research-summary",
        prompt_version="1.0.0",
        context_policy_id="project-only",
        budget=default_llm_budget(),
    )

    decision = evaluate_llm_route(
        request=request,
        providers=(_provider(),),
        estimated_input_tokens=1000,
        estimated_output_tokens=500,
    )

    assert decision.approved is True
    assert decision.provider_id == "local"
    assert decision.model_id == "local-small"
    assert decision.model_version == "2026-07"


def test_gateway_blocks_missing_capability() -> None:
    request = LLMRequestEnvelope(
        requested_capability=LLMCapability.TOOL_ORCHESTRATION,
        privacy_class=LLMPrivacyClass.INTERNAL,
        prompt_template_id="research-summary",
        prompt_version="1.0.0",
        context_policy_id="project-only",
        budget=default_llm_budget(),
    )

    decision = evaluate_llm_route(
        request=request,
        providers=(_provider(),),
        estimated_input_tokens=1000,
        estimated_output_tokens=500,
    )

    assert decision.approved is False
    assert decision.findings[0].code == "no_provider_route"


def test_gateway_blocks_cost_budget_excess() -> None:
    request = LLMRequestEnvelope(
        requested_capability=LLMCapability.SYNTHESIS,
        privacy_class=LLMPrivacyClass.INTERNAL,
        prompt_template_id="research-summary",
        prompt_version="1.0.0",
        context_policy_id="project-only",
        budget=default_llm_budget().model_copy(update={"max_cost_usd": 0.01}),
    )

    decision = evaluate_llm_route(
        request=request,
        providers=(_provider(),),
        estimated_input_tokens=8000,
        estimated_output_tokens=2000,
    )

    assert decision.approved is False
    assert any(finding.code == "cost_budget_exceeded" for finding in decision.findings)


def test_evaluation_report_fails_when_route_is_blocked() -> None:
    request = LLMRequestEnvelope(
        requested_capability=LLMCapability.SYNTHESIS,
        privacy_class=LLMPrivacyClass.INTERNAL,
        prompt_template_id="research-summary",
        prompt_version="1.0.0",
        context_policy_id="project-only",
        budget=default_llm_budget(),
    )
    route = evaluate_llm_route(
        request=request,
        providers=(),
        estimated_input_tokens=100,
        estimated_output_tokens=100,
    )

    report = build_llm_evaluation_report(
        request=request,
        route=route,
        dimensions=("grounding", "structured_output"),
        findings=(
            LLMFinding(
                code="route_blocked",
                severity=LLMFindingSeverity.ERROR,
                message="route was blocked before provider execution",
            ),
        ),
        cost_usd=0,
        latency_ms=0,
    )

    assert report.status.value == "failed"


def _provider() -> LLMProviderCapability:
    return LLMProviderCapability(
        provider_id="local",
        model_id="local-small",
        model_version="2026-07",
        capabilities=(LLMCapability.SYNTHESIS, LLMCapability.EXPLANATION),
        supported_privacy_classes=(LLMPrivacyClass.PUBLIC, LLMPrivacyClass.INTERNAL),
        available=True,
        cost_per_1k_input_tokens_usd=0.10,
        cost_per_1k_output_tokens_usd=0.20,
    )
