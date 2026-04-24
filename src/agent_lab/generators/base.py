"""Base class for code generation adapters.

Each adapter translates an ASL spec into a specific framework's codebase
(e.g. langchain-python, langgraph-python, native-go).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_lab.models.asl import AgenticArchitecture


class GeneratorAdapter(ABC):
    """Abstract base class that all code-generation adapters must implement.

    The adapter pattern allows AGENT-LAB to remain framework-agnostic:
    the ASL YAML is the single source of truth, and adapters translate
    it into framework-specific code.
    """

    name: str = ""

    @abstractmethod
    def generate(self, spec: AgenticArchitecture, output_dir: Path) -> list[Path]:
        """Generate code artifacts from the ASL spec.

        Args:
            spec: Validated AgenticArchitecture model.
            output_dir: Root directory for generated files.

        Returns:
            List of paths to generated files.
        """

    @abstractmethod
    def generate_dockerfile(self, spec: AgenticArchitecture, output_dir: Path) -> Path:
        """Generate a Dockerfile for the target agent/node.

        Args:
            spec: Validated AgenticArchitecture model.
            output_dir: Root directory for generated files.

        Returns:
            Path to the generated Dockerfile.
        """

    @abstractmethod
    def generate_k8s_manifests(self, spec: AgenticArchitecture, output_dir: Path) -> list[Path]:
        """Generate Kubernetes manifests (Helm or Kustomize).

        Args:
            spec: Validated AgenticArchitecture model.
            output_dir: Root directory for generated files.

        Returns:
            List of paths to generated manifest files.
        """
