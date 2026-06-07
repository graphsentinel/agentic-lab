# CLI Reference

> **`[IMPLEMENTED]`** — All three commands are shipped in the current release.

The `agentlab` CLI provides three commands for working with ASL specifications.

---

## Installation

```bash
pip install agentic-lab
```

Verify:

```bash
agentlab --help
```

---

## `agentlab init`

Scaffold a new agentic-lab project from a template.

```bash
agentlab init <name> --template <template>
```

### Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `<name>` | string | — | Project directory name |
| `--template` | `centralized`, `distributed` | `centralized` | Architecture template |

### Example

```bash
agentlab init my-hr-system --template centralized
```

Creates:

```
my-hr-system/
├── spec.yaml          # starter ASL spec (centralized template)
├── README.md
└── .gitignore
```

---

## `agentlab validate`

Validate an ASL YAML specification against the schema and check referential integrity.

```bash
agentlab validate <spec_file>
```

### What Is Validated

- **Schema conformance** — Pydantic model validation + JSON Schema
- **Referential integrity** — every agent `ToolBinding` resolves to a declared tool
- **Scope monotonicity** — delegated scope is a subset of delegator scope
- **Protocol consistency** — transport/auth combinations are valid
- **Edge sync** — model artifact source URLs are well-formed (when `edge_sync.enabled`)

### Example

```bash
agentlab validate examples/centralized_enterprise.yaml
```

**Success output**:

```
✓ Schema validation passed
✓ Referential integrity: 12 tool bindings resolved
✓ Scope monotonicity: 6 delegation edges validated
✓ Protocol consistency: grpc+spiffe-mtls OK
✓ spec is valid
```

**Error output**:

```
✗ Referential integrity error:
  Agent 'secure_db_query' references tool 'postgres_main_db'
  which is not declared in spec.layers.tools
  Declared tools: [postgres_hr_db, financial_data_api, web_search]
```

---

## `agentlab generate`

Generate framework-specific code and manifests from an ASL spec.

```bash
agentlab generate <spec_file> [OPTIONS]
```

### Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `<spec_file>` | path | — | ASL YAML specification file |
| `--output-dir` | path | `./output` | Directory for generated artifacts |
| `--framework` | `langchain_python`, `native_python` | from spec | Generator adapter |
| `--overwrite` | flag | false | Overwrite existing output directory |

### Example

```bash
agentlab generate examples/centralized_enterprise.yaml \
  --framework langchain_python \
  --output-dir ./output
```

**Generated artifacts** (LangChain target):

```
output/
├── agents/
│   ├── global_orchestrator.py
│   ├── hr_sub_orchestrator.py
│   ├── finance_sub_orchestrator.py
│   ├── secure_db_query.py
│   └── ...
├── tools/
│   ├── postgres_hr_db.py
│   ├── financial_data_api.py
│   └── web_search.py
├── manifests/
│   ├── deployment.yaml      # K8s Deployment manifests
│   ├── services.yaml        # K8s Service manifests
│   └── configmap.yaml       # ASL spec as ConfigMap
└── docker-compose.yml
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Validation error (spec invalid) |
| `2` | Generation error (output could not be written) |
| `3` | Configuration error (bad CLI flags) |

---

## See Also

- [Concepts → ASL](../concepts/asl.md) — spec format reference
- [Architecture → Package Structure](../architecture.md#package-structure) — generator internals
- [Examples](examples.md) — ready-to-use spec files
