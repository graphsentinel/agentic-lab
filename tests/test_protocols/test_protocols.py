"""Tests for protocol configuration models."""

from __future__ import annotations

from agent_lab.protocols.a2a import A2AProtocolConfig
from agent_lab.protocols.base import AuthMethod, GovernanceEngine, TransportType
from agent_lab.protocols.events import EventBroker, EventBusConfig
from agent_lab.protocols.mcp import MCPToolingConfig


class TestA2AProtocol:
    def test_defaults(self) -> None:
        cfg = A2AProtocolConfig()
        assert cfg.transport == TransportType.GRPC
        assert cfg.auth == AuthMethod.SPIFFE_MTLS
        assert cfg.governance == GovernanceEngine.OPA

    def test_distributed_config(self) -> None:
        cfg = A2AProtocolConfig(
            auth=AuthMethod.DID,
            governance=GovernanceEngine.SMART_CONTRACTS,
        )
        assert cfg.auth == AuthMethod.DID
        assert cfg.governance == GovernanceEngine.SMART_CONTRACTS


class TestMCPTooling:
    def test_defaults(self) -> None:
        cfg = MCPToolingConfig()
        assert cfg.sandboxed is True
        assert cfg.standard == "mcp"

    def test_rate_limit(self) -> None:
        cfg = MCPToolingConfig(rate_limit_rps=50)
        assert cfg.rate_limit_rps == 50


class TestEventBus:
    def test_defaults(self) -> None:
        cfg = EventBusConfig()
        assert cfg.broker == EventBroker.NATS
        assert cfg.spec == "cloudevents"

    def test_kafka_for_centralized(self) -> None:
        cfg = EventBusConfig(broker=EventBroker.KAFKA, topics=["invoices", "alerts"])
        assert cfg.broker == EventBroker.KAFKA
        assert len(cfg.topics) == 2
