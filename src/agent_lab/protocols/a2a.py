"""Agent-to-Agent (A2A / ACP) protocol configuration.

Governs delegation, negotiation, and peer-to-peer data sharing.
Enforced via gRPC interceptors and mutual TLS (mTLS).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from agent_lab.protocols.base import AuthMethod, GovernanceEngine, TransportType


class A2AProtocolConfig(BaseModel):
    """Configuration for agent-to-agent communication.

    Centralized (Template A): gRPC + SPIFFE-mTLS + OPA
    Distributed (Template B): gRPC + DID/VC + Smart Contracts
    """

    transport: TransportType = TransportType.GRPC
    auth: AuthMethod = AuthMethod.SPIFFE_MTLS
    governance: GovernanceEngine = GovernanceEngine.OPA
    enable_interceptors: bool = Field(
        default=True,
        description="Auto-generate gRPC interceptors for Agent Card validation",
    )
    protobuf_package: str = Field(
        default="agent_lab.a2a.v1",
        description="Protobuf package name for generated stubs",
    )
