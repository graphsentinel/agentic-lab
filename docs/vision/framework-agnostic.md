# Framework-Agnostic Core

> **`[PILOT-VALIDATED]`** — The adapter pattern and generator registry are implemented. Cross-framework enforcement seat composition is `[IN DEVELOPMENT]`.

A key design principle of agentic-lab: **governance must work across heterogeneous agent estates
without mandating a single runtime**.

---

## The Heterogeneity Problem

Real enterprise deployments use multiple agent frameworks:

- Team A uses **LangGraph** for complex reasoning workflows
- Team B uses **AutoGen** for multi-agent conversations
- Team C uses **native Python** for deterministic, high-throughput operations
- A partner organization uses **CrewAI** or **Google ADK**

Mandating a single framework is impractical. But per-framework governance creates silos,
inconsistent enforcement, and fragmented audit trails.

---

## The Framework-Agnostic Architecture

```
Shared Governance Core (runtime-agnostic)
    fingerprint → chain/graph → declared rules + learned baseline → score → verdict
    — emits gen_ai.agent.* OTel —
        ▲                                    │
   normalized events                    verdict
        │                                    ▼
   ADAPTER (per framework)          ENFORCEMENT SEAT (per runtime)
   • intra: ToolCall chain          • K8s: operator + MCP proxy
   • inter: AgentInteraction graph  • Docker: compose service proxy
                                    • Edge: in-process library
                                    • Library: score_chain() call
```

The contract between the governance core and each environment is minimal:

1. An **adapter** that emits normalized events (ToolCall or AgentInteraction)
2. An **enforcement seat** that can intercept and apply log/drop/block
3. An **OTLP endpoint** for telemetry export

Anything providing these three is a valid runtime.

---

## Adapter Pattern

Each framework gets a thin adapter that translates framework-native events into normalized governance events.

### LangChain / LangGraph Adapter

```python
from agent_lab.adapters import LangChainAdapter

adapter = LangChainAdapter(policy=GovernancePolicy.from_yaml("spec.yaml"))

# Wrap your LangChain tool with the governance adapter
governed_tool = adapter.wrap_tool(my_tool, agent_id="my_agent")
```

### Native Python Adapter

```python
from agent_lab.adapters import NativePythonAdapter

adapter = NativePythonAdapter(policy=GovernancePolicy.from_yaml("spec.yaml"))

@adapter.governed(agent_id="secure_db_query")
def run_query(sql: str) -> list[dict]:
    return db.execute(sql)
```

### Custom Adapter

Implement the `BaseAdapter` interface to support any framework:

```python
from agent_lab.generators.base import GeneratorAdapter
from agent_lab.models.asl import AgenticArchitecture

class MyFrameworkAdapter(GeneratorAdapter):
    name = "my_framework"

    def generate(self, spec: AgenticArchitecture, output_dir: Path) -> None:
        # Translate ASL spec → my framework's code/config
        ...
```

Register the adapter in the generator registry:

```python
from agent_lab.generators.registry import registry
registry.register(MyFrameworkAdapter())
```

---

## Enforcement Seats

The governance core emits a verdict (`log` / `drop` / `block`) for each tool call or
delegation event. The enforcement seat is responsible for acting on the verdict:

| Seat | Implementation | Latency |
|------|---------------|---------|
| **MCP Proxy sidecar** | Network proxy intercepting MCP calls | ~1-5ms |
| **In-process adapter** | Python decorator / wrapper | ~0.1-1ms |
| **A2A Proxy** | gRPC interceptor at trust boundary | ~2-10ms |
| **K8s Operator** | Reconcile-loop enforcement | Async |

---

## Normalized Event Schema

All adapters emit events in a common schema consumed by the governance core:

```python
@dataclass
class ToolCallEvent:
    agent_id: str              # from Agent Card
    tool_name: str
    operation: str             # read | write | execute | ...
    args: dict
    timestamp: datetime
    framework: str             # langchain | native | autogen | ...
    context: dict              # workflow step, parent delegation, etc.

@dataclass
class AgentInteractionEvent:
    source_agent_id: str
    target_agent_id: str
    interaction_type: str      # delegation | reporting | lateral | escalation
    scope: dict
    timestamp: datetime
```

---

## Generated Code Targets

The same ASL spec generates idiomatic code for each framework via the generator registry:

```bash
# LangChain / LangGraph (default)
agentlab generate spec.yaml --framework langchain_python

# Native Python (deterministic)
agentlab generate spec.yaml --framework native_python

# (future) AutoGen
agentlab generate spec.yaml --framework autogen

# (future) CrewAI
agentlab generate spec.yaml --framework crewai
```

---

## See Also

- [Architecture → Package Structure](../architecture.md#package-structure) — generator registry code location
- [Reference → CLI](../reference/cli.md) — `generate` command options
- [Vision → Federation](federation.md) — cross-org heterogeneity
- [Concepts → ASL](../concepts/asl.md#framework-agnostic-generation)
