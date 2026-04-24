"""Tests for the LangChain/LangGraph Python generator."""

from __future__ import annotations

from pathlib import Path

from agent_lab.generators.langchain_python import LangChainPythonGenerator
from agent_lab.models.asl import AgenticArchitecture


class TestLangChainPythonGenerator:
    def test_generate_creates_agent_and_tool_files(
        self, sample_spec: AgenticArchitecture, tmp_path: Path
    ) -> None:
        gen = LangChainPythonGenerator()
        files = gen.generate(sample_spec, tmp_path)
        # tools (2: mcp + langchain) + strategic (1) + tactical (1) + complex operators (1) = 5
        assert len(files) == 5
        assert all(f.exists() for f in files)
        tool_files = [f for f in files if "tools" in str(f)]
        agent_files = [f for f in files if "agents" in str(f) or "workers" in str(f)]
        assert len(tool_files) == 2
        assert len(agent_files) == 3

    def test_generate_dockerfile(
        self, sample_spec: AgenticArchitecture, tmp_path: Path
    ) -> None:
        gen = LangChainPythonGenerator()
        df = gen.generate_dockerfile(sample_spec, tmp_path)
        assert df.exists()
        content = df.read_text()
        assert "python:3.11" in content

    def test_generate_k8s_manifests(
        self, sample_spec: AgenticArchitecture, tmp_path: Path
    ) -> None:
        gen = LangChainPythonGenerator()
        manifests = gen.generate_k8s_manifests(sample_spec, tmp_path)
        # One manifest per agent (strategic + tactical + execution)
        assert len(manifests) == 4
        assert all(m.exists() for m in manifests)
