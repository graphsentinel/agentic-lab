"""Tests for Agent Card specification and access control."""

from __future__ import annotations

from agent_lab.models.agents import ReasoningType, SecurityClearance
from agent_lab.security.agent_card import AgentCardSpec


class TestAgentCardSpec:
    def test_high_security_deterministic(self) -> None:
        card = AgentCardSpec(
            agent_id="secure-worker-01",
            domain="finance",
            clearance=SecurityClearance.TOP_SECRET,
            reasoning=ReasoningType.DETERMINISTIC,
        )
        assert card.is_high_security() is True

    def test_high_clearance_llm_not_high_security(self) -> None:
        card = AgentCardSpec(
            agent_id="llm-agent-01",
            clearance=SecurityClearance.TOP_SECRET,
            reasoning=ReasoningType.LLM_BASED,
        )
        assert card.is_high_security() is False

    def test_low_clearance_not_high_security(self) -> None:
        card = AgentCardSpec(
            agent_id="public-agent",
            clearance=SecurityClearance.LOW_PUBLIC,
            reasoning=ReasoningType.DETERMINISTIC,
        )
        assert card.is_high_security() is False

    def test_can_access_same_level(self) -> None:
        card = AgentCardSpec(
            agent_id="agent-a",
            clearance=SecurityClearance.INTERNAL_RESTRICTED,
        )
        assert card.can_access(SecurityClearance.INTERNAL_RESTRICTED) is True

    def test_can_access_lower_level(self) -> None:
        card = AgentCardSpec(
            agent_id="agent-a",
            clearance=SecurityClearance.TOP_SECRET,
        )
        assert card.can_access(SecurityClearance.LOW_PUBLIC) is True

    def test_cannot_access_higher_level(self) -> None:
        card = AgentCardSpec(
            agent_id="agent-a",
            clearance=SecurityClearance.LOW_PUBLIC,
        )
        assert card.can_access(SecurityClearance.TOP_SECRET) is False
