"""Tests for the generator adapter registry."""

from __future__ import annotations

import pytest

from agent_lab.generators.registry import GeneratorRegistry


class TestGeneratorRegistry:
    def test_builtin_adapters_registered(self) -> None:
        import agent_lab.generators.langchain_python  # noqa: F401
        import agent_lab.generators.native_python  # noqa: F401

        available = GeneratorRegistry.available()
        assert "langchain-python" in available
        assert "langgraph-python" in available
        assert "native-python" in available

    def test_get_unknown_raises(self) -> None:
        with pytest.raises(KeyError, match="No generator adapter registered"):
            GeneratorRegistry.get("nonexistent-framework")
