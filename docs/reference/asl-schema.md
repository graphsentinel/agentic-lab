# ASL Schema Reference

> **`[IMPLEMENTED]`** — The Pydantic models (`src/agent_lab/models/`) are the authoritative schema definition.

This page is a field-level reference for the Agentic Specification Language (ASL).
For conceptual background, see [Concepts → ASL](../concepts/asl.md).

---

## Top-Level Resource

```yaml
apiVersion: agent-lab.io/v1alpha1   # required; must be this value
kind: AgenticArchitecture            # required; must be this value
metadata:                            # required
  name: string                       # required; unique identifier for this system
  labels:                            # optional; arbitrary key-value metadata
    key: value
spec:                                # required; system specification
  ...
```

---

## `spec`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `architecture_template` | `centralized` \| `distributed` | Yes | Topology template |
| `target_deployment` | `kubernetes` \| `edge` \| `hybrid` \| `docker` | Yes | Primary deployment target |
| `protocols` | [Protocols](#protocols) | Yes | Communication protocol configuration |
| `security` | [Security](#security) | Yes | Global security posture |
| `layers` | [Layers](#layers) | Yes | Agent hierarchy and tool catalogue |
| `generation` | [Generation](#generation) | No | Code generation parameters |
| `edge_sync` | [EdgeSync](#edge-sync) | No | Cloud-to-edge artifact sync |

---

## Protocols

```yaml
spec:
  protocols:
    internal_a2a:
      transport: grpc | http          # required
      auth: spiffe-mtls | did | jwt   # required
    event_bus: cloudevents | kafka | none
    tooling:
      standard: mcp | langchain | adk | native
      sandboxed: true | false         # default: false
```

---

## Security

```yaml
spec:
  security:
    default_clearance: low | medium | high | critical  # default: low
    pii_scrubbing: enabled | disabled                  # default: disabled
    audit_logging: none | retain_7_years | retain_1_year | retain_90_days
    deterministic_fallback: true | false               # default: false
    io_filtering: true | false                         # default: false
```

---

## Layers

### Tools Catalogue

```yaml
spec:
  layers:
    tools:
      - name: string            # required; unique within the catalogue
        type: string            # required; see Tool Types below
        framework: string       # required; mcp | langchain | adk | native
        description: string     # recommended
        language: python | go | typescript   # default: python
        permissions: [read, write, execute, delete, admin]   # default: [read]
        sandboxed: true | false # default: false
        input_schema:           # optional; typed input parameters
          - name: string
            type: string        # string | integer | number | boolean | object | array
            description: string
            required: true | false   # default: true
        output_schema:          # optional; typed output parameters
          - name: string
            type: string
            description: string
```

**Tool Types**:

| `type` | Description |
|--------|-------------|
| `api` | External service integration (REST, GraphQL) |
| `database` | Data store operations |
| `file_system` | File I/O operations |
| `search` | Information retrieval |
| `code_exec` | Code execution environments |
| `browser` | Web interaction |
| `custom` | User-defined capabilities |

### Strategic Layer

```yaml
spec:
  layers:
    strategic:
      - name: string                   # required; unique agent name
        description: string
        framework: langchain | native | autogen | crewai
        reasoning_type: llm | deterministic | predictive | graphrag
        clearance_level: low | medium | high | critical  # overrides security.default_clearance
        tools:                         # optional; subset of catalogue tools
          - name: string               # references a ToolDefinition
            permissions: [...]        # optional; narrows tool's default permissions
        delegates_to: [string]         # optional; list of tactical agent names
        lateral_peers: [string]        # optional; authorized lateral communication
```

### Tactical Layer

```yaml
spec:
  layers:
    tactical:
      - name: string
        description: string
        assigned_to: string            # required; name of strategic agent
        framework: string
        reasoning_type: string
        clearance_level: string
        tools:
          - name: string
            permissions: [...]
        delegates_to: [string]         # list of execution agent names
        lateral_peers: [string]
```

### Execution Layer

```yaml
spec:
  layers:
    execution:
      - name: string
        description: string
        assigned_to: string            # required; name of tactical agent
        framework: string
        reasoning_type: string
        clearance_level: string
        tools:
          - name: string
            permissions: [...]
        model_artifacts:               # optional; for edge / ML agents
          - type: onnx | gguf | torchscript | tflite | safetensors
            source: string             # s3:// or oci:// URI
            sync: true | false
```

---

## Generation

```yaml
spec:
  generation:
    framework: langchain_python | native_python   # default: langchain_python
    output_dir: string                            # default: ./output
    include_tests: true | false                   # default: true
    include_manifests: true | false               # default: true
```

---

## Edge Sync

```yaml
spec:
  edge_sync:
    enabled: true | false              # default: false
    transport: oci-pull | s3-sync | grpc-stream | mqtt
    interval_seconds: integer          # default: 3600
    registry: string                   # OCI registry URL or S3 bucket
    verify_signature: true | false     # default: true
    rollback_on_failure: true | false  # default: true
```

---

## See Also

- [Concepts → ASL](../concepts/asl.md) — conceptual overview with examples
- [Reference → Examples](examples.md) — complete annotated YAML examples
- [Reference → CLI](cli.md) — `validate` command for schema checking
