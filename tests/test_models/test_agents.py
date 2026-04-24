"""Tests for agent hierarchy models."""

from __future__ import annotations

from agent_lab.models.agents import (
    AgentCard,
    AgentType,
    ExecutionAgent,
    MCPToolPermission,
    ReasoningType,
    SecurityClearance,
    SecurityFilter,
    StrategicAgent,
    TacticalAgent,
)


class TestAgentCard:
    def test_default_card(self) -> None:
        card = AgentCard()
        assert card.clearance == SecurityClearance.LOW_PUBLIC
        assert card.reasoning == ReasoningType.DETERMINISTIC

    def test_delegation_list(self) -> None:
        card = AgentCard(can_delegate_to=["agent_a", "agent_b"])
        assert len(card.can_delegate_to) == 2


class TestStrategicAgent:
    def test_creation(self) -> None:
        agent = StrategicAgent(
            name="orchestrator",
            type=AgentType.LLM_REASONER,
            framework="langgraph-python",
        )
        assert agent.name == "orchestrator"
        assert agent.type == AgentType.LLM_REASONER


class TestTacticalAgent:
    def test_requires_domain_and_reports_to(self) -> None:
        agent = TacticalAgent(
            name="hr_agent",
            domain="human_resources",
            reports_to="orchestrator",
        )
        assert agent.domain == "human_resources"
        assert agent.reports_to == "orchestrator"


class TestExecutionAgent:
    def test_simple_operator(self) -> None:
        agent = ExecutionAgent(
            name="db_reader",
            type=AgentType.SIMPLE_OPERATOR,
            language="go",
            assigned_to="hr_agent",
            mcp_tools=[MCPToolPermission(name="postgres", permissions=["read"])],
        )
        assert agent.type == AgentType.SIMPLE_OPERATOR
        assert agent.mcp_tools[0].permissions == ["read"]

    def test_complex_operator_with_filters(self) -> None:
        agent = ExecutionAgent(
            name="writer",
            type=AgentType.COMPLEX_OPERATOR,
            assigned_to="hr_agent",
            security_filters=[
                SecurityFilter.PROMPT_INJECTION_SHIELD,
                SecurityFilter.PII_MASKER,
            ],
        )
        assert len(agent.security_filters) == 2
