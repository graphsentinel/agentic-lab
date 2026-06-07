# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2026-XX-XX

### Added

- **ASL (Agentic Specification Language)** — YAML schema with Pydantic models for defining multi-agent system architectures (`src/agent_lab/models/asl.py`)
- **Four-tier agent hierarchy** — Tools, Strategic, Tactical, Execution layers with explicit delegation and reporting relationships
- **Shared tools catalogue** — Declare tools once in `spec.layers.tools`; bind to agents with per-agent permission narrowing (`ToolBinding`)
- **Agent Card security model** — Per-agent identity specification with clearance levels and reasoning types (`src/agent_lab/security/agent_card.py`)
- **Edge sync configuration** — Cloud-to-edge artifact refresh via OCI pull, S3 sync, gRPC stream, and MQTT
- **Model artifacts** — ONNX, GGUF, TorchScript, TFLite, SafeTensors support for edge inference
- **Workflow artifacts** — Hot-reload orchestrator graphs for edge deployments
- **Code generators**:
    - LangChain/LangGraph Python adapter (`generators/langchain_python.py`)
    - Native Python deterministic adapter (`generators/native_python.py`)
- **Generator registry** — Adapter pattern for pluggable framework generators (`generators/registry.py`)
- **Protocol models**:
    - A2A (gRPC + mTLS) — `protocols/a2a.py`
    - MCP (sandboxed sidecar) — `protocols/mcp.py`
    - CloudEvents / Pub-Sub — `protocols/events.py`
- **Security governance** — PII scrubbing, audit retention, deterministic fallback, I/O filtering (`security/governance.py`)
- **CLI** — `agentlab init`, `agentlab validate`, `agentlab generate` (`cli.py`)
- **Example ASL specs**:
    - `examples/centralized_enterprise.yaml` — Enterprise HR/Finance/IT pyramid
    - `examples/distributed_mesh.yaml` — Supply-chain distributed mesh
    - `examples/edge_agent_workflow.yaml` — Factory-floor predictive maintenance on K3s
- **MkDocs documentation** — Full docs site with Concepts, Taxonomy, Topologies, Patterns, Vision, and Reference sections

---

*See the [GitHub releases page](https://github.com/graphsentinel/agentic-lab/releases) for tagged release notes.*
