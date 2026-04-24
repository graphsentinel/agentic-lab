"""Base protocol configuration models."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class TransportType(str, Enum):
    GRPC = "grpc"
    REST = "rest"
    NATS = "nats"


class AuthMethod(str, Enum):
    SPIFFE_MTLS = "spiffe-mtls"
    JWT = "jwt"
    DID = "did"
    API_KEY = "api-key"


class GovernanceEngine(str, Enum):
    OPA = "opa"
    SMART_CONTRACTS = "smart-contracts"
    LOCAL_POLICY = "local-policy"


class ProtocolConfig(BaseModel):
    """Base configuration for any communication protocol."""

    transport: TransportType = TransportType.GRPC
    auth: AuthMethod = AuthMethod.SPIFFE_MTLS


class ProtocolsConfig(BaseModel):
    """Top-level protocols block in the ASL spec."""

    internal_a2a: ProtocolConfig = Field(default_factory=ProtocolConfig)
    event_bus: str = Field(default="cloudevents", description="Event specification standard")
    tooling: ToolingConfig = Field(default_factory=lambda: ToolingConfig())


class ToolingConfig(BaseModel):
    """MCP tooling configuration."""

    standard: str = Field(default="mcp")
    sandboxed: bool = Field(
        default=True, description="Enforce network isolation for tool containers"
    )
