from osca.llm import (
    LLMCapability,
    LLMPrivacyClass,
    LLMProviderCapability,
    LLMRequestEnvelope,
    LLMPromptTemplate,
    SQLiteLLMLifecycleStore,
    build_llm_evaluation_report,
    default_llm_budget,
    evaluate_llm_route,
)


def test_llm_lifecycle_store_round_trips_request_scoped_records(tmp_path) -> None:
    store = SQLiteLLMLifecycleStore(tmp_path / "llm.sqlite3")
    store.initialize()
    provider = LLMProviderCapability(
        provider_id="local",
        model_id="local-small",
        model_version="2026-07",
        capabilities=(LLMCapability.SYNTHESIS,),
        supported_privacy_classes=(LLMPrivacyClass.INTERNAL,),
        available=True,
        cost_per_1k_input_tokens_usd=0,
        cost_per_1k_output_tokens_usd=0,
    )
    prompt = LLMPromptTemplate(
        prompt_id="research-summary",
        prompt_version="1.0.0",
        purpose="summarize",
        template_digest="sha256:abcdef",
    )
    request = LLMRequestEnvelope(
        requested_capability=LLMCapability.SYNTHESIS,
        privacy_class=LLMPrivacyClass.INTERNAL,
        prompt_template_id=prompt.prompt_id,
        prompt_version=prompt.prompt_version,
        context_policy_id="project-only",
        budget=default_llm_budget(),
    )
    route = evaluate_llm_route(
        request=request,
        providers=(provider,),
        estimated_input_tokens=100,
        estimated_output_tokens=100,
    )
    report = build_llm_evaluation_report(
        request=request,
        route=route,
        dimensions=("grounding",),
        cost_usd=0,
        latency_ms=25,
    )

    store.save_provider_capability(provider)
    store.save_prompt_template(prompt)
    store.save_request(request)
    store.save_route_decision(route)
    store.save_evaluation_report(report)

    assert store.list_provider_capabilities()[0].provider_id == "local"
    assert store.list_prompt_templates()[0].prompt_id == "research-summary"
    assert store.list_requests()[0].request_id == request.request_id
    assert (
        store.list_route_decisions(str(request.request_id))[0].route_decision_id
        == route.route_decision_id
    )
    assert (
        store.list_evaluation_reports(str(request.request_id))[0].evaluation_report_id
        == report.evaluation_report_id
    )
