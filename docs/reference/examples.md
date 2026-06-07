# Examples

Three ready-to-use ASL examples ship with agentic-lab. All live in the [`examples/`](https://github.com/graphsentinel/agentic-lab/tree/main/examples) directory.

---

## Centralized Enterprise

**File**: `examples/centralized_enterprise.yaml`  
**Template**: Centralized (Pyramid)  
**Target**: Kubernetes

A three-domain enterprise pyramid with an LLM orchestrator, three domain sub-orchestrators
(HR, Finance, IT), and deterministic execution-layer operators. Uses SPIFFE/mTLS, MCP
sandboxed sidecars, and 7-year audit retention.

**Topology**:

```
global_orchestrator  (Strategic — LLM)
├── hr_sub_orchestrator  (Tactical — LLM)
│   ├── secure_db_query         (Execution — Deterministic)
│   └── hr_report_generator     (Execution — LLM)
├── finance_sub_orchestrator  (Tactical — LLM)
│   ├── financial_analyst       (Execution — LLM)
│   └── budget_query            (Execution — Deterministic)
└── it_sub_orchestrator  (Tactical — LLM)
    ├── infra_monitor           (Execution — Deterministic)
    └── incident_responder      (Execution — LLM)
```

**Key features**:
- Shared tools catalogue (PostgreSQL HR DB, Financial API, web search, Slack notifications)
- Per-agent permission narrowing (HR operators get read-only DB; finance gets read-only Financial API)
- PII scrubbing enabled; deterministic fallback on LLM security violations
- All tools sandboxed in MCP sidecar containers

**Validate and generate**:

```bash
agentlab validate examples/centralized_enterprise.yaml
agentlab generate examples/centralized_enterprise.yaml \
  --framework langchain_python \
  --output-dir ./output/enterprise
```

---

## Distributed Mesh

**File**: `examples/distributed_mesh.yaml`  
**Template**: Distributed (Mesh)  
**Target**: Edge

A supply-chain mesh where warehouse, logistics, and fulfillment agents self-organize based
on capability. Uses Decentralized Identifiers (DIDs) for trust instead of a central identity provider.

**Topology** (peer-to-peer; no fixed hierarchy):

```
warehouse_agent ←→ logistics_agent ←→ fulfillment_agent
      ↕                                       ↕
route_planner_agent ←———————————→ inventory_optimizer_agent
```

**Key features**:
- DID-based authentication (no central SPIFFE/SPIRE dependency)
- Capability-based peer discovery
- Agents operate with intermittent connectivity (edge)
- CloudEvents event bus for async coordination

**Validate and generate**:

```bash
agentlab validate examples/distributed_mesh.yaml
agentlab generate examples/distributed_mesh.yaml \
  --framework native_python \
  --output-dir ./output/mesh
```

---

## Edge Predictive Maintenance

**File**: `examples/edge_agent_workflow.yaml`  
**Template**: Centralized (Edge)  
**Target**: Edge (K3s)

A factory-floor predictive maintenance system running on a constrained K3s edge node.
Models are pulled from OCI/S3 registries hourly. The vibration analyst uses a GGUF
small-language model for local inference; the anomaly detector uses ONNX.

**Topology**:

```
edge_orchestrator  (Strategic — LLM on GGUF)
└── floor_manager  (Tactical — Deterministic)
    ├── vibration_analyst   (Execution — Complex, GGUF SLM)
    └── anomaly_detector    (Execution — Predictive, ONNX)
```

**Key features**:
- OCI pull sync every hour; cosign signature verification
- Automatic rollback if new model fails health check
- GGUF small-language model for local inference (no cloud connectivity required)
- ONNX anomaly detector model refreshed from S3 as new versions publish
- OTLP exporter falls back to local logs when offline

**Validate and generate**:

```bash
agentlab validate examples/edge_agent_workflow.yaml
agentlab generate examples/edge_agent_workflow.yaml \
  --framework native_python \
  --output-dir ./output/edge
```

---

## Running the Examples

After generating, start the Docker Compose stack:

```bash
cd ./output/enterprise    # or ./output/mesh or ./output/edge
docker compose up
```

Or apply to Kubernetes:

```bash
kubectl apply -f ./output/enterprise/manifests/
```

---

## See Also

- [Reference → CLI](cli.md) — `validate` and `generate` command reference
- [Reference → ASL Schema](asl-schema.md) — field-level spec reference
- [Topologies → Pyramid](../topologies/pyramid.md) — centralized enterprise topology
- [Topologies → Mesh](../topologies/mesh.md) — distributed mesh topology
- [Topologies → Deployment Targets](../topologies/deployment-targets.md) — edge deployment
