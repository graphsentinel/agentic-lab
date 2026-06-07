# ASL — Agentic Specification Language

> **`[IMPLEMENTED]`** — ASL v1alpha1 is shipped and validated in the current release.

ASL is a declarative, YAML-based language for specifying multi-agent system architectures.
It uses **Kubernetes-style resource syntax** (`apiVersion`, `kind`, `metadata`, `spec`) and
defines the complete structure of an agentic system in a single, version-controlled artifact.

---

## Why ASL?

Current multi-agent frameworks require you to wire up agents in imperative code, scattered
across files and frameworks. This makes it hard to:

- Review or audit agent topology in a pull request
- Understand what tools each agent can access and what it can do with them
- Generate consistent deployment manifests (Docker, Kubernetes, edge) from a single source
- Enforce behavioral governance at the spec level

ASL solves this by making the architecture the source of truth.

---

## What ASL Encodes

| Concern | ASL field |
|---------|-----------|
| Agent hierarchy (strategic / tactical / execution) | `spec.layers` |
| Tool catalogue and capability types | `spec.layers.tools` |
| Per-agent tool bindings with permission narrowing | `agent.tools[].permissions` |
| Authorization and scope boundaries | `agent.scope` |
| Deployment target (K8s, edge, hybrid) | `spec.target_deployment` |
| Communication protocols (A2A, MCP, CloudEvents) | `spec.protocols` |
| Security posture (PII scrubbing, audit, fallback) | `spec.security` |
| Code-generation parameters | `spec.generation` |
| Edge artifact sync policy | `spec.edge_sync` |

---

## Skeleton

```yaml
apiVersion: agent-lab.io/v1alpha1
kind: AgenticArchitecture
metadata:
  name: my-system
  labels:
    environment: production
    template: centralized

spec:
  architecture_template: centralized   # or: distributed
  target_deployment: kubernetes         # or: edge, hybrid

  protocols:
    internal_a2a:
      transport: grpc
      auth: spiffe-mtls
    event_bus: cloudevents
    tooling:
      standard: mcp
      sandboxed: true

  security:
    default_clearance: low
    pii_scrubbing: enabled
    audit_logging: retain_7_years
    deterministic_fallback: true
    io_filtering: true

  layers:
    tools:      []   # shared tool catalogue — declared once
    strategic:  []   # global orchestrators
    tactical:   []   # domain sub-orchestrators
    execution:  []   # worker agents

  generation:
    framework: langchain_python   # or: native_python
    output_dir: ./output
```

---

## Tool Declaration { #tool-declaration }

Tools are **declared once** in `spec.layers.tools` and referenced by name from any agent.

```yaml
spec:
  layers:
    tools:
      - name: postgres_hr_db
        type: database             # api | database | file_system | search | code_exec | browser | custom
        framework: mcp             # mcp | langchain | adk | native
        description: Read-only access to the HR PostgreSQL database
        language: python
        permissions: [read]        # default permission set for this tool
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
```

### Tool Types

| Type | Description | Example |
|------|-------------|---------|
| `api` | External service integration | REST endpoints, GraphQL |
| `database` | Data store operations | PostgreSQL, MongoDB queries |
| `file_system` | File I/O | Read, write, list files |
| `search` | Information retrieval | Web search, vector search |
| `code_exec` | Code execution | Python REPL, sandboxed eval |
| `browser` | Web interaction | Page fetching, form filling |
| `custom` | User-defined | Domain-specific capabilities |

---

## Agent Definitions

### Strategic Agent

```yaml
spec:
  layers:
    strategic:
      - name: global_orchestrator
        description: Decomposes objectives and delegates to domain sub-orchestrators
        framework: langchain
        reasoning_type: llm
        tools:
          - name: web_search        # inherits tool's default permissions
        delegates_to:
          - hr_sub_orchestrator
          - finance_sub_orchestrator
```

### Tactical Agent

```yaml
spec:
  layers:
    tactical:
      - name: hr_sub_orchestrator
        description: Manages HR workflow execution agents
        assigned_to: global_orchestrator
        framework: langchain
        reasoning_type: llm
        tools:
          - name: postgres_hr_db
            permissions: [read]     # narrows from tool's default
        delegates_to:
          - secure_db_query
          - report_generator
```

### Execution Agent

```yaml
spec:
  layers:
    execution:
      - name: secure_db_query
        description: Deterministic SQL query executor
        assigned_to: hr_sub_orchestrator
        framework: native
        reasoning_type: deterministic   # zero hallucination
        tools:
          - name: postgres_hr_db
            permissions: [read]
```

---

## Edge Sync

When deploying to edge nodes, ASL supports a cloud-to-edge artifact refresh policy:

```yaml
spec:
  edge_sync:
    enabled: true
    transport: oci-pull
    interval_seconds: 3600
    registry: "oci://models.example.com/edge"
    verify_signature: true
    rollback_on_failure: true

  layers:
    execution:
      - name: anomaly_detector
        model_artifacts:
          - type: onnx
            source: "s3://ml-artifacts/anomaly-v2.onnx"
            sync: true
```

---

## Framework-Agnostic Generation

The same ASL spec generates code for multiple frameworks via pluggable adapters:

```bash
# LangChain / LangGraph
agentlab generate spec.yaml --framework langchain_python --output-dir ./output

# Native Python (deterministic)
agentlab generate spec.yaml --framework native_python --output-dir ./output
```

New adapters register themselves in the generator registry — see [Architecture → Package Structure](../architecture.md#package-structure).

---

## Validation

```bash
agentlab validate examples/centralized_enterprise.yaml
```

Validation checks:
- Schema conformance (Pydantic models + JSON Schema)
- Referential integrity (every agent tool binding resolves to a declared tool)
- Scope monotonicity (delegated scope is a subset of delegator scope)
- Protocol consistency (transport and auth combinations are valid)

---

## See Also

- [MABaC](mabac.md) — behavioral metadata extension to ASL
- [Authorization](authorization.md) — tool bindings as an authorization model
- [Architecture → ASL section](../architecture.md#asl-agentic-specification-language)
- [Examples](../reference/examples.md)
