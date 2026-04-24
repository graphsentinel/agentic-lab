# AGENT-LAB Architecture

## Overview

AGENT-LAB bridges abstract agentic system design and production-ready deployments through two phases:

1. **Phase 1 — Declarative Specification**: Define architecture, agents, tools, security, and protocols in YAML (ASL).
2. **Phase 2 — Code & Container Generation**: Translate ASL specs into framework-specific code, Dockerfiles, and K8s manifests.

## Four-Tier Hierarchy

AGENT-LAB uses a four-tier model: three agent layers plus a shared **Tools** catalogue.

```
Tools Catalogue (shared)       — Reusable capabilities available to any agent
    │
    ├── Strategic Layer (Boardroom)     — Global Orchestrators
    │       │
    │       ├── Tactical Layer (Management) — Domain Sub-Orchestrators
    │       │       │
    │       │       ├── Execution Layer (Workers)
    │       │       │       ├── Simple Operators  (deterministic, zero hallucination)
    │       │       │       └── Complex Operators (LLM, ML, GraphRAG)
```

### Tools Tier

Tools are reusable, framework-agnostic capability units — analogous to the tool
concept in MCP, LangChain, and Google ADK. They are **declared once** in the ASL
at `spec.layers.tools` and **referenced by name** from any agent via `tools[]`
bindings.

Each tool definition includes:

| Field | Purpose |
|-------|---------|
| `name` | Unique identifier used by agents' `tools[]` bindings |
| `type` | Capability class: `api`, `database`, `file_system`, `search`, `code_exec`, `browser`, `custom` |
| `framework` | Implementation target: `mcp`, `langchain`, `adk`, `native` |
| `language` | Implementation language (`python`, `go`, `typescript`) |
| `input_schema` | Typed input parameters the tool accepts |
| `output_schema` | Typed output parameters the tool returns |
| `permissions` | Default permission set (`read`, `write`, `execute`, `admin`) |
| `sandboxed` | Whether the tool runs in a network-isolated sidecar container |

Agents reference tools via `ToolBinding`:

```yaml
# On any agent (strategic, tactical, or execution):
tools:
  - name: postgres_hr_db          # references a ToolDefinition by name
    permissions: [read]           # optional: narrows the tool's default permissions
  - name: web_search              # inherits the tool's default permissions
```

This separation means:
- Tools are defined once and reused across the entire hierarchy
- Agents declare which tools they need (least-privilege)
- Per-agent permission overrides enforce fine-grained access control
- The code generator emits tool stubs matching the declared framework

## Package Structure

```
src/agent_lab/
├── __init__.py           # Package root, version
├── cli.py                # CLI entry points (init, validate, generate)
├── loader.py             # YAML loading utilities
├── models/
│   ├── asl.py            # Root AgenticArchitecture model
│   ├── agents.py         # Agent hierarchy (Strategic, Tactical, Execution)
│   └── tools.py          # Tool definitions and agent-side bindings
├── generators/
│   ├── base.py           # Abstract GeneratorAdapter
│   ├── registry.py       # Adapter registry
│   ├── langchain_python.py  # LangChain/LangGraph adapter
│   └── native_python.py     # Deterministic Python adapter
├── protocols/
│   ├── base.py           # Base protocol config
│   ├── a2a.py            # Agent-to-Agent (gRPC + mTLS)
│   ├── mcp.py            # Model Context Protocol (resource governance)
│   └── events.py         # CloudEvents / Pub-Sub
└── security/
    ├── governance.py      # Security config, governance policies
    └── agent_card.py      # Agent Card identity specification
```

## ASL (Agentic Specification Language)

The YAML-based ASL uses Kubernetes-style resource syntax:

```yaml
apiVersion: agent-lab.io/v1alpha1
kind: AgenticArchitecture
metadata:
  name: my-system
spec:
  architecture_template: centralized | distributed
  target_deployment: kubernetes | edge | hybrid
  protocols: { ... }
  security: { ... }
  layers:
    tools:      [ ... ]   # shared tool catalogue
    strategic:  [ ... ]   # global orchestrators
    tactical:   [ ... ]   # domain sub-orchestrators
    execution:  [ ... ]   # worker agents
  generation: { ... }
  edge_sync: { ... }      # cloud-to-edge artifact refresh (optional)
```

### Tool Declaration Example

```yaml
spec:
  layers:
    tools:
      - name: postgres_hr_db
        type: database
        framework: mcp
        description: Read-only access to the HR PostgreSQL database
        language: python
        permissions: [read]
        sandboxed: true
        input_schema:
          - name: query
            type: string
            description: SQL SELECT statement
        output_schema:
          - name: rows
            type: array
            description: Result rows

      - name: web_search
        type: search
        framework: langchain
        description: Internet search for public information
        language: python
        permissions: [read]

    strategic:
      - name: global_orchestrator
        tools:
          - name: web_search            # orchestrator can search the web

    execution:
      - name: secure_db_query
        assigned_to: hr_sub_orchestrator
        tools:
          - name: postgres_hr_db        # worker gets DB access
            permissions: [read]         # narrowed to read-only
```

## Security Model

- **A2A Governance**: gRPC interceptors + mTLS for agent-to-agent auth
- **MCP Resource Governance**: Sandboxed sidecar containers for tool access
- **Agent Cards**: Cryptographic identity (JWT or DID) with clearance levels
- **PII Scrubbing**: Auto-injected deterministic masking before LLM calls
- **Deterministic Fallback**: Auto-fallback on LLM security violations
- **Tool Sandboxing**: Tools run in network-isolated containers by default

## CLI

```bash
agentlab init <name> --template centralized
agentlab validate spec.yaml
agentlab generate spec.yaml --output-dir ./out
```
