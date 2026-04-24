"""Tests for edge sync, model artifacts, and workflow artifacts."""

from __future__ import annotations

from pathlib import Path

from agent_lab.models.agents import (
    AgentCard,
    AgentType,
    ExecutionAgent,
    ModelArtifact,
    ModelArtifactFormat,
    ReasoningType,
    SecurityClearance,
    StrategicAgent,
    WorkflowArtifact,
)
from agent_lab.models.asl import (
    AgenticArchitecture,
    EdgeSyncConfig,
    SyncTransport,
    TargetDeployment,
)


class TestModelArtifact:
    def test_onnx_artifact(self) -> None:
        art = ModelArtifact(
            name="anomaly-detector-v2",
            format=ModelArtifactFormat.ONNX,
            registry="s3://models/anomaly-detector",
            version="2.1.0",
            runtime="onnxruntime",
        )
        assert art.format == ModelArtifactFormat.ONNX
        assert art.version == "2.1.0"

    def test_gguf_slm_artifact(self) -> None:
        art = ModelArtifact(
            name="vibration-slm",
            format=ModelArtifactFormat.GGUF,
            runtime="llama-cpp",
        )
        assert art.format == ModelArtifactFormat.GGUF
        assert art.runtime == "llama-cpp"

    def test_defaults(self) -> None:
        art = ModelArtifact(name="default-model")
        assert art.format == ModelArtifactFormat.ONNX
        assert art.version == "latest"
        assert art.runtime == "onnxruntime"


class TestWorkflowArtifact:
    def test_creation(self) -> None:
        wf = WorkflowArtifact(
            name="edge-orchestrator-workflow",
            registry="oci://registry/workflows",
            version="1.0.0",
            format="langgraph-json",
        )
        assert wf.name == "edge-orchestrator-workflow"
        assert wf.version == "1.0.0"

    def test_defaults(self) -> None:
        wf = WorkflowArtifact(name="default-wf")
        assert wf.version == "latest"
        assert wf.format == "langgraph-json"


class TestEdgeSyncConfig:
    def test_disabled_by_default(self) -> None:
        cfg = EdgeSyncConfig()
        assert cfg.enabled is False

    def test_oci_pull_config(self) -> None:
        cfg = EdgeSyncConfig(
            enabled=True,
            transport=SyncTransport.OCI_PULL,
            interval_seconds=1800,
            registry="oci://my-registry/edge",
            verify_signature=True,
            rollback_on_failure=True,
        )
        assert cfg.enabled is True
        assert cfg.transport == SyncTransport.OCI_PULL
        assert cfg.interval_seconds == 1800

    def test_grpc_stream_push(self) -> None:
        cfg = EdgeSyncConfig(
            enabled=True,
            transport=SyncTransport.GRPC_STREAM,
            interval_seconds=0,  # push-based
        )
        assert cfg.interval_seconds == 0


class TestExecutionAgentWithModelArtifact:
    def test_predictive_agent_with_onnx(self) -> None:
        agent = ExecutionAgent(
            name="anomaly_detector",
            type=AgentType.PREDICTIVE,
            language="python",
            framework="native-python",
            assigned_to="floor_manager",
            agent_card=AgentCard(
                clearance=SecurityClearance.INTERNAL_RESTRICTED,
                reasoning=ReasoningType.DETERMINISTIC,
            ),
            model_artifact=ModelArtifact(
                name="anomaly-detector-v2",
                format=ModelArtifactFormat.ONNX,
                registry="s3://models/anomaly",
                runtime="onnxruntime",
            ),
        )
        assert agent.model_artifact is not None
        assert agent.model_artifact.format == ModelArtifactFormat.ONNX

    def test_complex_operator_with_slm(self) -> None:
        agent = ExecutionAgent(
            name="vibration_analyst",
            type=AgentType.COMPLEX_OPERATOR,
            framework="langchain-python",
            assigned_to="floor_manager",
            agent_card=AgentCard(reasoning=ReasoningType.LLM_BASED),
            model_artifact=ModelArtifact(
                name="vibration-slm",
                format=ModelArtifactFormat.GGUF,
                runtime="llama-cpp",
            ),
        )
        assert agent.model_artifact is not None
        assert agent.model_artifact.runtime == "llama-cpp"

    def test_agent_without_artifact(self) -> None:
        agent = ExecutionAgent(
            name="simple_worker",
            assigned_to="mgr",
        )
        assert agent.model_artifact is None


class TestStrategicAgentWithWorkflowArtifact:
    def test_orchestrator_with_workflow(self) -> None:
        agent = StrategicAgent(
            name="edge_orchestrator",
            workflow_artifact=WorkflowArtifact(
                name="edge-wf",
                registry="oci://reg/wf",
                version="2.0.0",
            ),
        )
        assert agent.workflow_artifact is not None
        assert agent.workflow_artifact.version == "2.0.0"

    def test_orchestrator_without_workflow(self) -> None:
        agent = StrategicAgent(name="cloud_orchestrator")
        assert agent.workflow_artifact is None


class TestEdgeExampleYAMLRoundTrip:
    """Load the edge_agent_workflow.yaml example and validate it."""

    def test_load_edge_example(self) -> None:
        example = Path(__file__).parent.parent.parent / "examples" / "edge_agent_workflow.yaml"
        if not example.exists():
            # Fall back if running from a different cwd
            return
        arch = AgenticArchitecture.from_yaml(example)
        assert arch.metadata.name == "edge-predictive-maintenance"
        assert arch.spec.target_deployment == TargetDeployment.EDGE
        assert arch.spec.edge_sync.enabled is True
        assert arch.spec.edge_sync.transport == SyncTransport.OCI_PULL
        assert arch.spec.edge_sync.verify_signature is True

        # Check agents
        assert len(arch.spec.layers.strategic) == 1
        orch = arch.spec.layers.strategic[0]
        assert orch.workflow_artifact is not None
        assert orch.workflow_artifact.name == "edge-orchestrator-workflow"

        assert len(arch.spec.layers.execution) == 2
        vibration = next(a for a in arch.spec.layers.execution if a.name == "vibration_analyst")
        anomaly = next(a for a in arch.spec.layers.execution if a.name == "anomaly_detector")

        assert vibration.model_artifact is not None
        assert vibration.model_artifact.format == ModelArtifactFormat.GGUF

        assert anomaly.model_artifact is not None
        assert anomaly.model_artifact.format == ModelArtifactFormat.ONNX
        assert anomaly.type == AgentType.PREDICTIVE
