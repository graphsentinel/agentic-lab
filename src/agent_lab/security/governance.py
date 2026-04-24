"""Security, privacy, and governance configuration.

Implements defense-in-depth strategy governing both A2A workflows
and Agent-to-Resource (MCP) interactions.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class PIIScrubbing(str, Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"


class AuditRetention(str, Enum):
    RETAIN_1_YEAR = "retain_1_year"
    RETAIN_3_YEARS = "retain_3_years"
    RETAIN_7_YEARS = "retain_7_years"


class SecurityConfig(BaseModel):
    """Global security posture for the architecture.

    Centralized (Template A): OPA-based RBAC/ABAC with PII scrubbing.
    Distributed (Template B): Sovereign Privacy with Smart Contract audit.
    """

    default_clearance: str = Field(
        default="low",
        description="Default security clearance for agents without explicit assignment",
    )
    pii_scrubbing: PIIScrubbing = Field(
        default=PIIScrubbing.ENABLED,
        description="Auto-inject deterministic masking before LLM calls",
    )
    audit_logging: AuditRetention = Field(
        default=AuditRetention.RETAIN_7_YEARS,
        description="Audit log retention policy",
    )
    deterministic_fallback: bool = Field(
        default=True,
        description="Auto-fallback to deterministic agent on LLM security violation",
    )
    io_filtering: bool = Field(
        default=True,
        description="Scan incoming prompts and outgoing generations for adversarial patterns",
    )


class GovernancePolicy(BaseModel):
    """A reusable governance policy definition.

    Policies can be referenced by name in agent cards and layer configs.
    """

    name: str
    description: str = ""
    engine: str = Field(
        default="opa",
        description="Policy engine (opa, smart-contracts, local-policy)",
    )
    rules: list[str] = Field(
        default_factory=list,
        description="List of policy rule identifiers",
    )
