from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from osca.llm import (
    LLMCapability,
    LLMContextPolicy,
    LLMEvaluationReport,
    LLMEvaluationStatus,
    LLMFinding,
    LLMFindingSeverity,
    LLMPrivacyClass,
    LLMPromptTemplate,
    LLMProviderCapability,
    LLMRequestEnvelope,
    LLMRouteDecision,
    LLMStructuredOutputContract,
    LLMToolDefinition,
    LLMToolMode,
    default_llm_budget,
)


def test_provider_capability_requires_timezone_aware_declaration() -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        LLMProviderCapability(
            provider_id="local",
            model_id="local-small",
            model_version="2026-07",
            capabilities=(LLMCapability.SYNTHESIS,),
            supported_privacy_classes=(LLMPrivacyClass.INTERNAL,),
            available=True,
            cost_per_1k_input_tokens_usd=0,
            cost_per_1k_output_tokens_usd=0,
            declared_at=datetime(2026, 1, 1),
        )


def test_llm_tool_rejects_live_order_capability() -> None:
    with pytest.raises(ValidationError, match="live-order"):
        LLMToolDefinition(
            tool_id="paper.place-live-order",
            tool_version="1.0.0",
            mode=LLMToolMode.STATE_CHANGING,
            permission_scope="orders",
            allows_live_orders=True,
            requires_confirmation=True,
        )


def test_state_changing_tool_requires_confirmation() -> None:
    with pytest.raises(ValidationError, match="confirmation"):
        LLMToolDefinition(
            tool_id="project.update-thesis",
            tool_version="1.0.0",
            mode=LLMToolMode.STATE_CHANGING,
            permission_scope="project",
            requires_confirmation=False,
        )


def test_prompt_template_requires_digest_algorithm_prefix() -> None:
    with pytest.raises(ValidationError, match="algorithm prefix"):
        LLMPromptTemplate(
            prompt_id="research-summary",
            prompt_version="1.0.0",
            purpose="summarize",
            template_digest="abcdef",
        )


def test_context_policy_rejects_unrelated_project_history() -> None:
    with pytest.raises(ValidationError, match="unrelated project"):
        LLMContextPolicy(
            context_policy_id="project-only",
            selected_project_id=uuid4(),
            allow_unrelated_project_history=True,
            untrusted_content_handling="quote-and-summarize",
        )


def test_structured_output_requires_strict_validation() -> None:
    with pytest.raises(ValidationError, match="strict validation"):
        LLMStructuredOutputContract(
            output_contract_id="finding-json",
            schema_version="1.0.0",
            schema_digest="sha256:abcdef",
            strict_validation=False,
        )


def test_sensitive_request_requires_disclosure_approval() -> None:
    with pytest.raises(ValidationError, match="sensitive"):
        LLMRequestEnvelope(
            requested_capability=LLMCapability.EXPLANATION,
            privacy_class=LLMPrivacyClass.SENSITIVE,
            prompt_template_id="research-summary",
            prompt_version="1.0.0",
            context_policy_id="project-only",
            budget=default_llm_budget(),
        )


def test_approved_route_requires_exact_model_identity() -> None:
    with pytest.raises(ValidationError, match="exact provider"):
        LLMRouteDecision(
            request_id=uuid4(),
            provider_id=None,
            model_id=None,
            model_version=None,
            approved=True,
            rationale="missing identity",
            estimated_cost_usd=0,
        )


def test_passed_evaluation_rejects_error_findings() -> None:
    with pytest.raises(ValidationError, match="error findings"):
        LLMEvaluationReport(
            request_id=uuid4(),
            route_decision_id=uuid4(),
            status=LLMEvaluationStatus.PASSED,
            evaluated_dimensions=("grounding",),
            findings=(
                LLMFinding(
                    code="ungrounded_claim",
                    severity=LLMFindingSeverity.ERROR,
                    message="claim lacks supporting evidence",
                ),
            ),
            cost_usd=0,
            latency_ms=10,
        )
