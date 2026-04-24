"""Tool definitions for the Tools tier.

Tools are reusable, framework-agnostic capability units that can be bound to
any agent across the Strategic, Tactical, or Execution layers. This is
analogous to the tool concept in MCP, LangChain, Google ADK, and similar
frameworks — but declared once in the ASL and referenced by name from agents.

Tools are defined at the architecture level (``spec.layers.tools``) so they
form a shared catalogue.  Each agent then declares which tools it uses via a
``tools`` list of :class:`ToolBinding` references that can override
permissions per-agent.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ToolType(str, Enum):
    """Classification of tool capability."""

    API = "api"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    SEARCH = "search"
    CODE_EXEC = "code_exec"
    BROWSER = "browser"
    CUSTOM = "custom"


class ToolFramework(str, Enum):
    """Framework / protocol the tool is implemented against."""

    MCP = "mcp"
    LANGCHAIN = "langchain"
    ADK = "adk"
    NATIVE = "native"


# ---------------------------------------------------------------------------
# Input / Output schemas (lightweight declaration)
# ---------------------------------------------------------------------------


class ToolParameter(BaseModel):
    """A single parameter in a tool's input or output schema."""

    name: str = Field(..., description="Parameter name")
    type: str = Field(default="string", description="JSON-Schema type (string, integer, …)")
    description: str = Field(default="", description="Human-readable description")
    required: bool = Field(default=True)


# ---------------------------------------------------------------------------
# Tool definition
# ---------------------------------------------------------------------------


class ToolDefinition(BaseModel):
    """A reusable tool declared in the ASL tools catalogue.

    Example YAML::

        tools:
          - name: postgres_hr_db
            type: database
            framework: mcp
            description: Read-only access to the HR PostgreSQL database
            language: python
            input_schema:
              - name: query
                type: string
                description: SQL SELECT statement
            output_schema:
              - name: rows
                type: array
                description: Result rows
    """

    name: str = Field(..., description="Unique tool identifier, referenced by agents via tools[]")
    type: ToolType = Field(
        default=ToolType.CUSTOM,
        description="Capability classification",
    )
    framework: ToolFramework = Field(
        default=ToolFramework.MCP,
        description="Implementation framework / protocol",
    )
    description: str = Field(default="", description="Human-readable summary of what the tool does")
    language: str = Field(
        default="python",
        description="Implementation language (python, go, typescript)",
    )
    version: str = Field(default="0.1.0", description="Semantic version of this tool")
    input_schema: list[ToolParameter] = Field(
        default_factory=list,
        description="Typed input parameters the tool accepts",
    )
    output_schema: list[ToolParameter] = Field(
        default_factory=list,
        description="Typed output parameters the tool returns",
    )
    permissions: list[str] = Field(
        default_factory=lambda: ["read"],
        description="Default permission set (read, write, execute, admin)",
    )
    sandboxed: bool = Field(
        default=True,
        description="Run inside a sandboxed sidecar (network-isolated container)",
    )
    rate_limit_rps: int = Field(
        default=0,
        description="Max requests per second (0 = unlimited)",
    )
    metadata: dict[str, str] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Tool binding (agent-side reference)
# ---------------------------------------------------------------------------


class ToolBinding(BaseModel):
    """A reference from an agent to a tool in the shared catalogue.

    Agents declare which tools they use via ``tools: [ToolBinding, ...]``.
    The binding can narrow the default permissions to enforce least-privilege.

    Example YAML (on an agent)::

        tools:
          - name: postgres_hr_db
            permissions: [read]
          - name: web_search
    """

    name: str = Field(
        ..., description="Name of a ToolDefinition declared in spec.layers.tools"
    )
    permissions: list[str] | None = Field(
        default=None,
        description="Override permissions for this agent (None = inherit tool defaults)",
    )
