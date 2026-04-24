"""LangChain/LangGraph Python code generation adapter.

Generates Python code targeting LangChain or LangGraph for:
- Strategic Orchestrators (LangGraph stateful agents)
- Tactical Sub-Orchestrators
- Complex Operators (LLM-based workers)
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from agent_lab.generators.base import GeneratorAdapter
from agent_lab.generators.registry import GeneratorRegistry

if TYPE_CHECKING:
    from agent_lab.models.asl import AgenticArchitecture


class LangChainPythonGenerator(GeneratorAdapter):
    """Generates Python code using LangChain/LangGraph framework."""

    name = "langchain-python"

    def generate(self, spec: AgenticArchitecture, output_dir: Path) -> list[Path]:
        """Generate LangChain/LangGraph Python agent code."""
        generated: list[Path] = []
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build a lookup of tool definitions by name
        tool_defs = {t.name: t for t in spec.spec.layers.tools}

        # Generate tool modules
        for tool in spec.spec.layers.tools:
            if tool.framework.value in ("langchain", "mcp"):
                path = output_dir / "tools" / f"{tool.name}.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(self._render_tool(tool, spec))
                generated.append(path)

        # Generate strategic agents
        for agent in spec.spec.layers.strategic:
            path = output_dir / "agents" / f"{agent.name}.py"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self._render_strategic_agent(agent, spec))
            generated.append(path)

        # Generate tactical agents
        for agent in spec.spec.layers.tactical:
            path = output_dir / "agents" / f"{agent.name}.py"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self._render_tactical_agent(agent, spec))
            generated.append(path)

        # Generate execution agents (complex operators only; simple operators use native)
        for agent in spec.spec.layers.execution:
            if agent.type.value in ("complex_operator", "llm_reasoner", "graph_rag"):
                path = output_dir / "workers" / f"{agent.name}.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(self._render_execution_agent(agent, spec))
                generated.append(path)

        return generated

    def generate_dockerfile(self, spec: AgenticArchitecture, output_dir: Path) -> Path:
        """Generate a Python-based Dockerfile."""
        path = output_dir / "Dockerfile"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "FROM python:3.11-slim\n"
            "WORKDIR /app\n"
            "COPY requirements.txt .\n"
            "RUN pip install --no-cache-dir -r requirements.txt\n"
            "COPY . .\n"
            'CMD ["python", "-m", "agent"]\n'
        )
        return path

    def generate_k8s_manifests(self, spec: AgenticArchitecture, output_dir: Path) -> list[Path]:
        """Generate Kubernetes deployment manifests."""
        manifests_dir = output_dir / "k8s"
        manifests_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []

        all_agents = (
            list(spec.spec.layers.strategic)
            + list(spec.spec.layers.tactical)
            + list(spec.spec.layers.execution)
        )
        for agent in all_agents:
            path = manifests_dir / f"{agent.name}-deployment.yaml"
            path.write_text(
                f"apiVersion: apps/v1\n"
                f"kind: Deployment\n"
                f"metadata:\n"
                f"  name: {agent.name}\n"
                f"  labels:\n"
                f"    app: {agent.name}\n"
                f"spec:\n"
                f"  replicas: 1\n"
                f"  selector:\n"
                f"    matchLabels:\n"
                f"      app: {agent.name}\n"
                f"  template:\n"
                f"    metadata:\n"
                f"      labels:\n"
                f"        app: {agent.name}\n"
                f"    spec:\n"
                f"      containers:\n"
                f"      - name: {agent.name}\n"
                f'        image: "{spec.metadata.name}/{agent.name}:latest"\n'
            )
            generated.append(path)

        return generated

    # ------------------------------------------------------------------
    # Private rendering helpers (templates will be expanded in Phase 2)
    # ------------------------------------------------------------------

    @staticmethod
    def _tool_imports(agent: object) -> str:
        """Generate import lines for tools bound to an agent."""
        bindings = getattr(agent, "tools", [])
        if not bindings:
            return ""
        imports = "\n".join(
            f"from tools.{b.name} import {b.name}" for b in bindings
        )
        return f"\n# --- Tool imports ---\n{imports}\n"

    @staticmethod
    def _render_tool(tool: object, spec: AgenticArchitecture) -> str:
        """Generate a tool module stub."""
        name = getattr(tool, "name", "tool")
        desc = getattr(tool, "description", "")
        framework = getattr(tool, "framework", None)
        fw_val = framework.value if framework else "mcp"
        inputs = getattr(tool, "input_schema", [])
        outputs = getattr(tool, "output_schema", [])

        input_comment = ""
        if inputs:
            input_comment = "    # Input parameters:\n"
            for p in inputs:
                input_comment += f"    #   {p.name}: {p.type} — {p.description}\n"

        output_comment = ""
        if outputs:
            output_comment = "    # Output parameters:\n"
            for p in outputs:
                output_comment += f"    #   {p.name}: {p.type} — {p.description}\n"

        if fw_val == "langchain":
            return (
                f'"""Tool: {name} — {desc}"""\n'
                f"\n"
                f"# Auto-generated by AGENT-LAB — {spec.metadata.name}\n"
                f"# Framework: LangChain Tool\n"
                f"\n"
                f"from langchain.tools import tool\n"
                f"\n"
                f"\n"
                f"@tool\n"
                f"def {name}(**kwargs) -> dict:\n"
                f'    """{desc}"""\n'
                f"{input_comment}"
                f"{output_comment}"
                f"    raise NotImplementedError\n"
            )
        else:
            # MCP / generic tool stub
            return (
                f'"""Tool: {name} — {desc}"""\n'
                f"\n"
                f"# Auto-generated by AGENT-LAB — {spec.metadata.name}\n"
                f"# Framework: {fw_val}\n"
                f"\n"
                f"\n"
                f"class {name.replace('_', ' ').title().replace(' ', '')}Tool:\n"
                f'    """{desc}"""\n'
                f"\n"
                f"    def invoke(self, **kwargs) -> dict:\n"
                f'        """Execute the tool."""\n'
                f"{input_comment}"
                f"{output_comment}"
                f"        raise NotImplementedError\n"
            )

    @staticmethod
    def _render_strategic_agent(agent: object, spec: AgenticArchitecture) -> str:
        name = getattr(agent, "name", "agent")
        tool_imports = LangChainPythonGenerator._tool_imports(agent)
        return (
            f'"""Strategic Orchestrator: {name}"""\n'
            f"\n"
            f"# Auto-generated by AGENT-LAB — {spec.metadata.name}\n"
            f"# Framework: LangGraph\n"
            f"# This agent performs high-level planning and workflow decomposition.\n"
            f"\n"
            f"from langgraph.graph import StateGraph\n"
            f"{tool_imports}\n"
            f"\n"
            f"def build_{name}_graph():\n"
            f'    """Build the LangGraph state machine for {name}."""\n'
            f"    graph = StateGraph(dict)\n"
            f"    # TODO: Define nodes and edges per ASL spec\n"
            f"    return graph.compile()\n"
        )

    @staticmethod
    def _render_tactical_agent(agent: object, spec: AgenticArchitecture) -> str:
        name = getattr(agent, "name", "agent")
        domain = getattr(agent, "domain", "general")
        tool_imports = LangChainPythonGenerator._tool_imports(agent)
        return (
            f'"""Tactical Sub-Orchestrator: {name} (domain: {domain})"""\n'
            f"\n"
            f"# Auto-generated by AGENT-LAB — {spec.metadata.name}\n"
            f"\n"
            f"from langgraph.graph import StateGraph\n"
            f"{tool_imports}\n"
            f"\n"
            f"def build_{name}_graph():\n"
            f'    """Build the domain workflow for {name}."""\n'
            f"    graph = StateGraph(dict)\n"
            f"    # TODO: Define domain-specific nodes and edges\n"
            f"    return graph.compile()\n"
        )

    @staticmethod
    def _render_execution_agent(agent: object, spec: AgenticArchitecture) -> str:
        name = getattr(agent, "name", "worker")
        tool_imports = LangChainPythonGenerator._tool_imports(agent)
        return (
            f'"""Complex Operator: {name}"""\n'
            f"\n"
            f"# Auto-generated by AGENT-LAB — {spec.metadata.name}\n"
            f"\n"
            f"from langchain.agents import AgentExecutor\n"
            f"{tool_imports}\n"
            f"\n"
            f"def create_{name}_agent() -> AgentExecutor:\n"
            f'    """Create the LangChain agent executor for {name}."""\n'
            f"    # TODO: Configure LLM, tools, and prompt template\n"
            f"    raise NotImplementedError\n"
        )


# Self-register with the global registry
GeneratorRegistry.register("langchain-python", LangChainPythonGenerator)
GeneratorRegistry.register("langgraph-python", LangChainPythonGenerator)
