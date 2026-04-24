"""Agent hierarchy models covering all three tiers.

- Strategic Layer: Global Orchestrators
- Tactical Layer: Domain Sub-Orchestrators
- Execution Layer: Simple Operators (deterministic) and Complex Operators (LLM/ML)
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from agent_lab.models.tools import ToolBinding


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class AgentType(str, Enum):
    """Classification of agent reasoning capability."""

    LLM_REASONER = "llm_reasoner"
    SIMPLE_OPERATOR = "simple_operator"
    COMPLEX_OPERATOR = "complex_operator"
    PREDICTIVE = "predictive"
    GRAPH_RAG = "graph_rag"


class ReasoningType(str, Enum):
    """Whether an agent is deterministic or LLM-based.

    High-security tasks strictly require `deterministic`.
    """

    DETERMINISTIC = "deterministic"
    LLM_BASED = "llm-based"


class SecurityClearance(str, Enum):
    """Agent security clearance levels (ascending privilege)."""

    LOW_PUBLIC = "low-public"
    INTERNAL_RESTRICTED = "internal-restricted"
    CONFIDENTIAL = "confidential"
    TOP_SECRET = "top-secret"


# ---------------------------------------------------------------------------
# Agent Card
# ---------------------------------------------------------------------------


class ModelArtifactFormat(str, Enum):
    """Supported ML model artifact formats for edge deployment."""

    ONNX = "onnx"
    TORCHSCRIPT = "torchscript"
    TFLITE = "tflite"
    GGUF = "gguf"
    SAFETENSORS = "safetensors"


class ModelArtifact(BaseModel):
    """Reference to an ML model or SLM artifact used by an agent.

    On edge deployments, model artifacts are pulled from a cloud registry
    and refreshed according to the EdgeSyncConfig schedule.
    """

    name: str = Field(..., description="Logical model name (e.g. anomaly-detector-v2)")
    format: ModelArtifactFormat = Field(
        default=ModelArtifactFormat.ONNX,
        description="Serialization format",
    )
    registry: str = Field(
        default="",
        description="Model registry URI (e.g. s3://models/, oci://registry/models)",
    )
    version: str = Field(
        default="latest",
        description="Pinned version or 'latest' for auto-update",
    )
    runtime: str = Field(
        default="onnxruntime",
        description="Inference runtime (onnxruntime, vllm, llama-cpp, triton)",
    )


class MCPToolPermission(BaseModel):
    """A single MCP tool binding with explicit permissions."""

    name: str = Field(..., description="MCP tool/server name")
    permissions: list[str] = Field(
        default_factory=lambda: ["read"],
        description="Allowed operations (read, write, execute)",
    )


class AgentCard(BaseModel):
    """Cryptographically-signed identity document for zero-trust A2A communication.

    In Centralized architectures this maps to a JWT.
    In Distributed Mesh architectures this maps to a Verifiable Credential / DID.
    """

    clearance: SecurityClearance = Field(
        default=SecurityClearance.LOW_PUBLIC,
        description="Security clearance level",
    )
    reasoning: ReasoningType = Field(
        default=ReasoningType.DETERMINISTIC,
        description="Agent reasoning type",
    )
    capabilities: list[str] = Field(
        default_factory=list,
        description="Standardized list of what the agent can do",
    )
    can_delegate_to: list[str] = Field(
        default_factory=list,
        description="Agent names this agent may delegate tasks to",
    )
    requires_mcp_auth: bool = Field(
        default=False,
        description="Whether MCP auth is required for resource access",
    )


# ---------------------------------------------------------------------------
# Security filters (for Complex Operators)
# ---------------------------------------------------------------------------


class SecurityFilter(str, Enum):
    """Pre/post-processing security filters injected around LLM calls."""

    PROMPT_INJECTION_SHIELD = "prompt_injection_shield"
    PII_MASKER = "pii_masker"
    OUTPUT_VALIDATOR = "output_validator"


# ---------------------------------------------------------------------------
# Agent definitions per tier
# ---------------------------------------------------------------------------


class BaseAgent(BaseModel):
    """Fields common to every agent regardless of tier."""

    name: str = Field(..., description="Unique agent identifier")
    agent_card: AgentCard = Field(default_factory=AgentCard)
    tools: list[ToolBinding] = Field(
        default_factory=list,
        description="Tools this agent can use, referencing entries in spec.layers.tools",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowArtifact(BaseModel):
    """Reference to a versioned workflow definition that can be synced to edge nodes.

    On edge deployments the orchestrator's workflow graph is pulled from a
    cloud registry so that edge nodes can receive updated orchestration logic
    without a full container redeploy.
    """

    name: str = Field(..., description="Logical workflow name")
    registry: str = Field(
        default="",
        description="Artifact registry URI (e.g. s3://workflows/, oci://registry/workflows)",
    )
    version: str = Field(
        default="latest",
        description="Pinned version or 'latest' for auto-update",
    )
    format: str = Field(
        default="langgraph-json",
        description="Serialization format (langgraph-json, dag-yaml, state-machine-json)",
    )


class StrategicAgent(BaseAgent):
    """Global Orchestrator — the Boardroom.

    High-level planning, workflow decomposition, global state management.
    Deploys Delegate and Aggregate patterns to manage Sub-Orchestrators.
    """

    type: AgentType = Field(default=AgentType.LLM_REASONER)
    framework: str = Field(
        default="langgraph-python",
        description="Agent framework (e.g. langgraph-python, autogen-python)",
    )
    workflow_artifact: WorkflowArtifact | None = Field(
        default=None,
        description="Versioned workflow definition — enables cloud-to-edge workflow refresh",
    )


class TacticalAgent(BaseAgent):
    """Domain Sub-Orchestrator — the Management.

    Receives assignments from the Strategic layer, manages domain-specific
    resources, and reports status back up the chain.
    """

    domain: str = Field(..., description="Business domain (e.g. human_resources, finance)")
    reports_to: str = Field(..., description="Name of the strategic agent this reports to")
    framework: str = Field(default="langgraph-python")


class ExecutionAgent(BaseAgent):
    """Worker agent — Simple Operator or Complex Operator.

    Simple Operators are deterministic (zero hallucination risk).
    Complex Operators are LLM-based, Predictive (ML), or GraphRAG.
    """

    type: AgentType = Field(default=AgentType.SIMPLE_OPERATOR)
    language: str = Field(
        default="python",
        description="Implementation language (python or go)",
    )
    framework: str = Field(
        default="native-python",
        description="Framework for this worker (e.g. langchain-python, native-go)",
    )
    assigned_to: str = Field(
        ...,
        description="Name of the tactical agent managing this worker",
    )
    mcp_tools: list[MCPToolPermission] = Field(
        default_factory=list,
        description="MCP tool bindings with explicit permission scoping",
    )
    security_filters: list[SecurityFilter] = Field(
        default_factory=list,
        description="Pre/post-processing security filters for LLM-based agents",
    )
    model_artifact: ModelArtifact | None = Field(
        default=None,
        description="ML/SLM model artifact — enables cloud-to-edge model refresh",
    )
