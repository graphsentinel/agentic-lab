"""Tests for the tools tier — ToolDefinition, ToolBinding, and agent integration."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_lab.models.agents import (
    AgentCard,
    AgentType,
    ExecutionAgent,
    ReasoningType,
    SecurityClearance,
    StrategicAgent,
    TacticalAgent,
)
from agent_lab.models.asl import AgenticArchitecture
from agent_lab.models.tools import (
    ToolBinding,
    ToolDefinition,
    ToolFramework,
    ToolParameter,
    ToolType,
)


# ---------------------------------------------------------------------------
# ToolDefinition
# ---------------------------------------------------------------------------


class TestToolDefinition:
    def test_minimal_tool(self) -> None:
        tool = ToolDefinition(name="my_tool")
        assert tool.name == "my_tool"
        assert tool.type == ToolType.CUSTOM
        assert tool.framework == ToolFramework.MCP
        assert tool.permissions == ["read"]
        assert tool.sandboxed is True

    def test_database_tool(self) -> None:
        tool = ToolDefinition(
            name="postgres_hr_db",
            type=ToolType.DATABASE,
            framework=ToolFramework.MCP,
            description="Read-only HR database",
            language="python",
            permissions=["read"],
            input_schema=[
                ToolParameter(name="query", type="string", description="SQL SELECT"),
            ],
            output_schema=[
                ToolParameter(name="rows", type="array", description="Result rows"),
            ],
        )
        assert tool.type == ToolType.DATABASE
        assert len(tool.input_schema) == 1
        assert len(tool.output_schema) == 1
        assert tool.input_schema[0].name == "query"

    def test_langchain_tool(self) -> None:
        tool = ToolDefinition(
            name="web_search",
            type=ToolType.SEARCH,
            framework=ToolFramework.LANGCHAIN,
            description="Internet search",
        )
        assert tool.framework == ToolFramework.LANGCHAIN

    def test_native_tool(self) -> None:
        tool = ToolDefinition(
            name="email_sender",
            type=ToolType.API,
            framework=ToolFramework.NATIVE,
            permissions=["execute"],
        )
        assert tool.framework == ToolFramework.NATIVE
        assert tool.permissions == ["execute"]

    def test_adk_tool(self) -> None:
        tool = ToolDefinition(
            name="code_runner",
            type=ToolType.CODE_EXEC,
            framework=ToolFramework.ADK,
        )
        assert tool.framework == ToolFramework.ADK

    def test_all_tool_types(self) -> None:
        for tt in ToolType:
            tool = ToolDefinition(name=f"tool_{tt.value}", type=tt)
            assert tool.type == tt

    def test_rate_limit(self) -> None:
        tool = ToolDefinition(name="limited", rate_limit_rps=50)
        assert tool.rate_limit_rps == 50

    def test_version(self) -> None:
        tool = ToolDefinition(name="versioned", version="2.3.1")
        assert tool.version == "2.3.1"

    def test_metadata(self) -> None:
        tool = ToolDefinition(name="tagged", metadata={"team": "platform"})
        assert tool.metadata["team"] == "platform"


# ---------------------------------------------------------------------------
# ToolParameter
# ---------------------------------------------------------------------------


class TestToolParameter:
    def test_defaults(self) -> None:
        p = ToolParameter(name="x")
        assert p.type == "string"
        assert p.required is True
        assert p.description == ""

    def test_optional_param(self) -> None:
        p = ToolParameter(name="limit", type="integer", required=False)
        assert p.required is False


# ---------------------------------------------------------------------------
# ToolBinding
# ---------------------------------------------------------------------------


class TestToolBinding:
    def test_minimal_binding(self) -> None:
        b = ToolBinding(name="postgres_hr_db")
        assert b.name == "postgres_hr_db"
        assert b.permissions is None  # inherit from tool default

    def test_binding_with_override(self) -> None:
        b = ToolBinding(name="warehouse_db", permissions=["read"])
        assert b.permissions == ["read"]


# ---------------------------------------------------------------------------
# Agent tool bindings across all tiers
# ---------------------------------------------------------------------------


class TestAgentToolBindings:
    def test_strategic_agent_with_tools(self) -> None:
        agent = StrategicAgent(
            name="orchestrator",
            tools=[
                ToolBinding(name="web_search"),
                ToolBinding(name="alert_notifier"),
            ],
        )
        assert len(agent.tools) == 2
        assert agent.tools[0].name == "web_search"

    def test_tactical_agent_with_tools(self) -> None:
        agent = TacticalAgent(
            name="hr_manager",
            domain="hr",
            reports_to="orchestrator",
            tools=[ToolBinding(name="email_sender")],
        )
        assert len(agent.tools) == 1

    def test_execution_agent_with_tools(self) -> None:
        agent = ExecutionAgent(
            name="db_reader",
            assigned_to="hr_manager",
            tools=[
                ToolBinding(name="postgres_hr_db", permissions=["read"]),
            ],
        )
        assert len(agent.tools) == 1
        assert agent.tools[0].permissions == ["read"]

    def test_agent_without_tools(self) -> None:
        agent = StrategicAgent(name="bare_orchestrator")
        assert agent.tools == []


# ---------------------------------------------------------------------------
# Tools in LayersConfig / full spec round-trip
# ---------------------------------------------------------------------------


class TestToolsInSpec:
    def test_layers_tools_list(self, sample_spec: AgenticArchitecture) -> None:
        """sample_spec fixture now includes tools."""
        assert len(sample_spec.spec.layers.tools) > 0

    def test_yaml_round_trip_preserves_tools(
        self, sample_spec: AgenticArchitecture, tmp_path: Path
    ) -> None:
        path = tmp_path / "tools_rt.yaml"
        sample_spec.to_yaml(path)
        loaded = AgenticArchitecture.from_yaml(path)

        assert len(loaded.spec.layers.tools) == len(sample_spec.spec.layers.tools)
        orig_tool = sample_spec.spec.layers.tools[0]
        loaded_tool = loaded.spec.layers.tools[0]
        assert loaded_tool.name == orig_tool.name
        assert loaded_tool.type == orig_tool.type
        assert loaded_tool.framework == orig_tool.framework
        assert len(loaded_tool.input_schema) == len(orig_tool.input_schema)

    def test_agent_tool_bindings_survive_round_trip(
        self, sample_spec: AgenticArchitecture, tmp_path: Path
    ) -> None:
        path = tmp_path / "bindings_rt.yaml"
        sample_spec.to_yaml(path)
        loaded = AgenticArchitecture.from_yaml(path)

        # Strategic agent should have tool bindings
        orch = loaded.spec.layers.strategic[0]
        assert len(orch.tools) > 0


# ---------------------------------------------------------------------------
# Example YAML validation
# ---------------------------------------------------------------------------


class TestExampleYAMLsWithTools:
    """Validate that updated example YAMLs load correctly with tools."""

    _examples_dir = Path(__file__).parent.parent.parent / "examples"

    def test_centralized_example(self) -> None:
        path = self._examples_dir / "centralized_enterprise.yaml"
        if not path.exists():
            return
        arch = AgenticArchitecture.from_yaml(path)
        assert len(arch.spec.layers.tools) == 4
        tool_names = {t.name for t in arch.spec.layers.tools}
        assert "postgres_hr_db" in tool_names
        assert "web_search" in tool_names
        assert "email_sender" in tool_names
        # Verify agent bindings
        orch = arch.spec.layers.strategic[0]
        assert any(b.name == "web_search" for b in orch.tools)

    def test_distributed_example(self) -> None:
        path = self._examples_dir / "distributed_mesh.yaml"
        if not path.exists():
            return
        arch = AgenticArchitecture.from_yaml(path)
        assert len(arch.spec.layers.tools) == 3
        # transport_manager should have tools
        tm = next(a for a in arch.spec.layers.tactical if a.name == "transport_manager")
        assert len(tm.tools) == 2

    def test_edge_example(self) -> None:
        path = self._examples_dir / "edge_agent_workflow.yaml"
        if not path.exists():
            return
        arch = AgenticArchitecture.from_yaml(path)
        assert len(arch.spec.layers.tools) == 3
        tool_names = {t.name for t in arch.spec.layers.tools}
        assert "sensor_timeseries_db" in tool_names
        assert "maintenance_ticket_api" in tool_names
        assert "alert_notifier" in tool_names
        # anomaly_detector should bind 2 tools
        ad = next(a for a in arch.spec.layers.execution if a.name == "anomaly_detector")
        assert len(ad.tools) == 2
