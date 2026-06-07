# Roles

> **`[IMPLEMENTED]`** — Role models are shipped. Cross-cutting Monitor and Gatekeeper roles are `[IN DEVELOPMENT]`.

This page defines the agent roles used across the four-tier hierarchy in agentic-lab.

---

## Role Definitions

| Role | Layer | Description |
|------|-------|-------------|
| **Orchestrator** | Strategic | Decomposes objectives, delegates tasks, aggregates results |
| **Sub-Orchestrator** | Tactical | Manages a bounded domain; coordinates execution agents |
| **Simple Operator** | Execution | Executes deterministic, well-defined operations |
| **Complex Operator** | Execution | Executes tasks requiring LLM reasoning or ML inference |
| **Monitor** | Cross-cutting | Observes system behavior and reports anomalies (read-only) |
| **Gatekeeper** | Cross-cutting | Enforces policies at trust boundaries (approve/deny) |

---

## Four-Tier Hierarchy

```
Tools Catalogue (shared)
    │
    ├── Strategic Layer — Orchestrators
    │       Decompose high-level objectives → domain sub-tasks
    │       Framework: LangGraph, AutoGen (LLM-powered)
    │       Scope: broadest — can delegate to any tactical agent
    │
    ├── Tactical Layer — Sub-Orchestrators
    │       Receive delegated tasks → coordinate execution
    │       Framework: LangGraph, native Python
    │       Scope: bounded per domain (HR, Finance, IT...)
    │
    └── Execution Layer — Operators
            ├── Simple Operators  (deterministic, zero hallucination)
            │       Framework: native Python, rule engines
            │       Use for: file I/O, SQL queries, API calls, config ops
            │
            └── Complex Operators (LLM, ML, GraphRAG)
                    Framework: LangChain, ONNX inference, GraphRAG
                    Use for: reasoning, generation, anomaly detection
```

---

## Strategic Layer — Orchestrator

**Role**: Global orchestrators that decompose high-level objectives into domain-specific sub-tasks.

**Characteristics**:
- Broadest scope; can delegate to any tactical agent
- Typically LLM-powered with planning capabilities
- Aggregates results from sub-orchestrators
- Does not perform direct execution — delegates everything

**ASL Example**:

```yaml
strategic:
  - name: global_orchestrator
    description: Decomposes enterprise objectives and delegates to domain sub-orchestrators
    framework: langchain
    reasoning_type: llm
    tools:
      - name: web_search
    delegates_to:
      - hr_sub_orchestrator
      - finance_sub_orchestrator
      - it_sub_orchestrator
```

---

## Tactical Layer — Sub-Orchestrator

**Role**: Domain sub-orchestrators that receive delegated tasks and coordinate execution within their domain.

**Characteristics**:
- Scope bounded to a single domain (HR, Finance, Legal, IT)
- Manages a team of execution-layer operators
- May itself be LLM-powered for within-domain reasoning
- Can communicate laterally with peer sub-orchestrators (if declared in ASL)

**ASL Example**:

```yaml
tactical:
  - name: hr_sub_orchestrator
    description: Coordinates HR workflow execution agents
    assigned_to: global_orchestrator
    framework: langchain
    reasoning_type: llm
    tools:
      - name: postgres_hr_db
        permissions: [read]
    delegates_to:
      - secure_db_query
      - report_generator
```

---

## Execution Layer — Simple Operator

**Role**: Deterministic agents that perform well-defined operations with predictable, auditable behavior.

**Characteristics**:
- Zero hallucination risk (no LLM in the path)
- Uses rule-based or imperative logic
- High throughput; suitable for sandboxed tool calls
- Primary target: file I/O, database queries, API calls, config operations

**ASL Example**:

```yaml
execution:
  - name: secure_db_query
    description: Deterministic SQL query executor
    assigned_to: hr_sub_orchestrator
    framework: native
    reasoning_type: deterministic
    tools:
      - name: postgres_hr_db
        permissions: [read]
```

---

## Execution Layer — Complex Operator

**Role**: LLM- or ML-powered agents that handle tasks requiring reasoning, generation, or inference.

**Characteristics**:
- Inherent stochasticity — primary target for [behavioral envelopes](../concepts/behavioral-envelope.md)
- Supports LLM, ONNX inference, GGUF small-language models, GraphRAG
- Higher latency and cost than Simple Operators
- Requires explicit governance contract in MABaC

**ASL Example**:

```yaml
execution:
  - name: vibration_analyst
    description: Analyses vibration sensor readings for anomaly patterns
    assigned_to: floor_manager
    framework: langchain
    reasoning_type: llm
    model_artifacts:
      - type: gguf
        source: "oci://factory-models.example.com/edge/vibration-7b.gguf"
        sync: true
    tools:
      - name: sensor_data_api
        permissions: [read]
```

---

## Cross-Cutting Roles

### Monitor

A read-only observer that spans the hierarchy. Monitors consume events from any layer,
detect anomalies, and emit alerts — but cannot modify agent behavior directly.

### Gatekeeper

An enforcement agent at trust boundaries. Gatekeepers intercept cross-agent calls,
apply policy verdicts (approve/deny), and emit OTel attribution. They are the
runtime embodiment of the [Behavioral Envelope](../concepts/behavioral-envelope.md).

---

## See Also

- [Interaction Patterns](interaction-patterns.md) — how roles communicate
- [Architecture → Four-Tier Hierarchy](../architecture.md#four-tier-hierarchy)
- [ASL → Agent Definitions](../concepts/asl.md#agent-definitions)
