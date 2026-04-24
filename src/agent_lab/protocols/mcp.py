"""Model Context Protocol (MCP) tooling configuration.

MCP governs what an individual agent can actually do to the outside world
(databases, file systems, external APIs). Acts as a sandbox limiting blast radius.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MCPToolingConfig(BaseModel):
    """Configuration for MCP-based tool access.

    Each MCP tool runs as a sidecar container with strict read/write boundaries.
    The LLM agent container communicates over localhost to the MCP sidecar.
    """

    standard: str = Field(default="mcp")
    sandboxed: bool = Field(
        default=True,
        description="Enforce network isolation for tool containers",
    )
    sidecar_image: str = Field(
        default="",
        description="Base container image for MCP sidecar (empty = auto-detect)",
    )
    rate_limit_rps: int = Field(
        default=100,
        description="Max requests per second to external resources",
    )
