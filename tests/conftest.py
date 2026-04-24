"""Shared test fixtures for AGENT-LAB test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_lab.models.agents import (
    AgentCard,
    AgentType,
    ExecutionAgent,
    MCPToolPermission,
    ReasoningType,
    SecurityClearance,
    SecurityFilter,
    StrategicAgent,
    TacticalAgent,
)
from agent_lab.models.tools import (
    ToolBinding,
    ToolDefinition,
    ToolFramework,
    ToolParameter,
    ToolType,
)
from agent_lab.models.asl import (
    API_VERSION,
    KIND,
    AgenticArchitecture,
    ArchitectureTemplate,
    GenerationConfig,
    LayersConfig,
    Metadata,
    SpecConfig,
    TargetDeployment,
)
from agent_lab.protocols.base import ProtocolsConfig
from agent_lab.security.governance import SecurityConfig


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def sample_spec() -> AgenticArchitecture:
    """Build a minimal but complete ASL spec for testing."""
    return AgenticArchitecture(
        apiVersion=API_VERSION,
        kind=KIND,
        metadata=Metadata(name="test-architecture"),
        spec=SpecConfig(
            architecture_template=ArchitectureTemplate.CENTRALIZED,
            target_deployment=TargetDeployment.KUBERNETES,
            protocols=ProtocolsConfig(),
            security=SecurityConfig(),
            layers=LayersConfig(
                tools=[
                    ToolDefinition(
                        name="postgres_hr_db",
                        type=ToolType.DATABASE,
                        framework=ToolFramework.MCP,
                        description="Read-only access to the HR PostgreSQL database",
                        language="python",
                        permissions=["read"],
                        sandboxed=True,
                        input_schema=[
                            ToolParameter(
                                name="query",
                                type="string",
                                description="SQL SELECT statement",
                            ),
                        ],
                        output_schema=[
                            ToolParameter(
                                name="rows",
                                type="array",
                                description="Result rows",
                            ),
                        ],
                    ),
                    ToolDefinition(
                        name="web_search",
                        type=ToolType.SEARCH,
                        framework=ToolFramework.LANGCHAIN,
                        description="Internet search",
                        language="python",
                        permissions=["read"],
                    ),
                ],
                strategic=[
                    StrategicAgent(
                        name="global_orchestrator",
                        type=AgentType.LLM_REASONER,
                        framework="langgraph-python",
                        agent_card=AgentCard(
                            clearance=SecurityClearance.TOP_SECRET,
                            reasoning=ReasoningType.LLM_BASED,
                            can_delegate_to=[
                                "hr_sub_orchestrator",
                                "finance_sub_orchestrator",
                            ],
                        ),
                        tools=[
                            ToolBinding(name="web_search"),
                        ],
                    )
                ],
                tactical=[
                    TacticalAgent(
                        name="hr_sub_orchestrator",
                        domain="human_resources",
                        reports_to="global_orchestrator",
                        agent_card=AgentCard(
                            clearance=SecurityClearance.INTERNAL_RESTRICTED,
                            requires_mcp_auth=True,
                        ),
                    )
                ],
                execution=[
                    ExecutionAgent(
                        name="secure_db_query",
                        type=AgentType.SIMPLE_OPERATOR,
                        language="python",
                        framework="native-python",
                        assigned_to="hr_sub_orchestrator",
                        agent_card=AgentCard(
                            clearance=SecurityClearance.TOP_SECRET,
                            reasoning=ReasoningType.DETERMINISTIC,
                        ),
                        tools=[
                            ToolBinding(
                                name="postgres_hr_db", permissions=["read"]
                            ),
                        ],
                        mcp_tools=[
                            MCPToolPermission(
                                name="postgres_hr_db", permissions=["read"]
                            )
                        ],
                    ),
                    ExecutionAgent(
                        name="generative_writer",
                        type=AgentType.COMPLEX_OPERATOR,
                        language="python",
                        framework="langchain-python",
                        assigned_to="hr_sub_orchestrator",
                        agent_card=AgentCard(
                            clearance=SecurityClearance.LOW_PUBLIC,
                            reasoning=ReasoningType.LLM_BASED,
                        ),
                        tools=[
                            ToolBinding(name="web_search"),
                        ],
                        security_filters=[
                            SecurityFilter.PROMPT_INJECTION_SHIELD,
                            SecurityFilter.PII_MASKER,
                        ],
                    ),
                ],
            ),
            generation=GenerationConfig(
                target_framework="langchain-python",
            ),
        ),
    )


@pytest.fixture()
def sample_spec_yaml(sample_spec: AgenticArchitecture, tmp_path: Path) -> Path:
    """Write the sample spec to a temporary YAML file and return its path."""
    path = tmp_path / "asl.yaml"
    sample_spec.to_yaml(path)
    return path
