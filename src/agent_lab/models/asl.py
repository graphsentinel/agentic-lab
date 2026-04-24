"""Root ASL (Agentic Specification Language) model.

Defines the top-level AgenticArchitecture that users declare in YAML.
Corresponds to: apiVersion: agent-lab.io/v1alpha1, kind: AgenticArchitecture
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Annotated, Any

import yaml
from pydantic import BaseModel, Field

from agent_lab.models.agents import ExecutionAgent, StrategicAgent, TacticalAgent
from agent_lab.models.tools import ToolDefinition
from agent_lab.protocols.base import ProtocolsConfig
from agent_lab.security.governance import SecurityConfig


class ArchitectureTemplate(str, Enum):
    """Supported architecture templates from Phase 1 Discovery."""

    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"


class TargetDeployment(str, Enum):
    """Deployment target environments."""

    KUBERNETES = "kubernetes"
    EDGE = "edge"
    HYBRID = "hybrid"
    DOCKER_COMPOSE = "docker-compose"


class TargetLanguage(str, Enum):
    """Supported code generation target languages."""

    PYTHON = "python"
    GO = "go"


class Metadata(BaseModel):
    """Standard metadata for an ASL document."""

    name: str = Field(..., description="Unique name for this architecture")
    labels: dict[str, str] = Field(default_factory=dict)
    annotations: dict[str, str] = Field(default_factory=dict)


class LayersConfig(BaseModel):
    """Four-tier hierarchy: agents across three layers plus a shared tools catalogue."""

    tools: list[ToolDefinition] = Field(
        default_factory=list,
        description="Shared tool catalogue — reusable capabilities available to any agent",
    )
    strategic: list[StrategicAgent] = Field(
        default_factory=list,
        description="Global orchestrator agents (the Boardroom)",
    )
    tactical: list[TacticalAgent] = Field(
        default_factory=list,
        description="Domain sub-orchestrators (the Management)",
    )
    execution: list[ExecutionAgent] = Field(
        default_factory=list,
        description="Worker agents — simple operators and complex operators",
    )


class SyncTransport(str, Enum):
    """Transport mechanism for cloud-to-edge artifact sync."""

    OCI_PULL = "oci-pull"
    S3_SYNC = "s3-sync"
    GRPC_STREAM = "grpc-stream"
    MQTT = "mqtt"


class EdgeSyncConfig(BaseModel):
    """Cloud-to-edge synchronization policy.

    Defines how edge-deployed agents receive updated artifacts (ML models,
    orchestrator workflows, policy bundles) from a cloud registry without
    requiring a full container redeploy.
    """

    enabled: bool = Field(
        default=False,
        description="Enable periodic cloud-to-edge artifact sync",
    )
    transport: SyncTransport = Field(
        default=SyncTransport.OCI_PULL,
        description="How artifacts are delivered to edge nodes",
    )
    interval_seconds: int = Field(
        default=3600,
        description="Polling interval in seconds (0 = push-based via event_bus)",
    )
    registry: str = Field(
        default="",
        description="Default artifact registry URI (can be overridden per-agent)",
    )
    verify_signature: bool = Field(
        default=True,
        description="Require cryptographic signature verification on pulled artifacts",
    )
    rollback_on_failure: bool = Field(
        default=True,
        description="Auto-rollback to previous version if the new artifact fails health checks",
    )


class GenerationConfig(BaseModel):
    """Parameters controlling code generation (Phase 2)."""

    target_language: TargetLanguage = Field(
        default=TargetLanguage.PYTHON,
        description="Primary language for generated code",
    )
    target_framework: str = Field(
        default="langchain-python",
        description="Agent framework to generate for (e.g. langchain-python, langgraph-python, native-go)",
    )
    output_dir: str = Field(
        default="./generated",
        description="Directory for generated artifacts",
    )
    containerize: bool = Field(
        default=True,
        description="Generate Dockerfiles for each agent",
    )
    k8s_manifests: bool = Field(
        default=True,
        description="Generate Kubernetes manifests (Helm/Kustomize)",
    )


class SpecConfig(BaseModel):
    """The spec block of an AgenticArchitecture document."""

    architecture_template: ArchitectureTemplate
    target_deployment: TargetDeployment = TargetDeployment.KUBERNETES
    protocols: ProtocolsConfig = Field(default_factory=ProtocolsConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    layers: LayersConfig = Field(default_factory=LayersConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    edge_sync: EdgeSyncConfig = Field(
        default_factory=EdgeSyncConfig,
        description="Cloud-to-edge artifact sync policy (ML models, workflows, policies)",
    )


API_VERSION = "agent-lab.io/v1alpha1"
KIND = "AgenticArchitecture"


class AgenticArchitecture(BaseModel):
    """Root model for an ASL YAML document.

    Example:
        apiVersion: agent-lab.io/v1alpha1
        kind: AgenticArchitecture
        metadata:
          name: my-architecture
        spec:
          architecture_template: centralized
          ...
    """

    apiVersion: Annotated[str, Field(default=API_VERSION)]  # noqa: N815
    kind: Annotated[str, Field(default=KIND)]
    metadata: Metadata
    spec: SpecConfig

    @classmethod
    def from_yaml(cls, path: str | Path) -> AgenticArchitecture:
        """Load and validate an ASL document from a YAML file."""
        with open(path) as f:
            data: dict[str, Any] = yaml.safe_load(f)
        return cls.model_validate(data)

    def to_yaml(self, path: str | Path) -> None:
        """Serialize the architecture to a YAML file."""
        data = self.model_dump(mode="json")
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
