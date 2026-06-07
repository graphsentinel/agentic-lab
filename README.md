# agentic-lab

[![CI](https://github.com/graphsentinel/agentic-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/graphsentinel/agentic-lab/actions)
[![PyPI](https://img.shields.io/pypi/v/agentic-lab)](https://pypi.org/project/agentic-lab/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/agentic-lab)](https://pypi.org/project/agentic-lab/)

**Declarative agentic workflow architecture and automated code/container generation.**

agentic-lab lets you define complex multi-agent systems in YAML using the
**Agent Specification Language (ASL)**, then generate framework-specific
Python code, Dockerfiles, and Kubernetes manifests.

## Key Features

- **Declarative ASL** — Kubernetes-style YAML for agentic architectures
- **Four-tier hierarchy** — Tools catalogue + Strategic + Tactical + Execution layers
- **Shared tools catalogue** — Declare tools once, bind to agents with per-agent permissions
- **Security governance** — Agent Cards with clearance levels, PII scrubbing, audit retention
- **Deterministic orchestrators** — Zero-hallucination routing for high-security contexts
- **Edge deployment** — Cloud-to-edge model sync (OCI pull), offline inference, model artifacts (ONNX, GGUF)
- **Code generation** — LangChain/LangGraph and native Python adapters with extensible registry
- **Protocol models** — A2A (gRPC+mTLS), MCP (sandboxed sidecar), CloudEvents

## Quick Start

    # Install
    pip install agentic-lab

    # Or install from source
    pip install -e ".[dev]"

    # Scaffold a new project
    agentlab init my-project --template centralized

    # Validate an ASL spec
    agentlab validate examples/centralized_enterprise.yaml

    # Generate code and manifests
    agentlab generate examples/centralized_enterprise.yaml --output-dir ./output

## Examples

| Example | Template | Description |
|---------|----------|-------------|
| `centralized_enterprise.yaml` | Centralized | Enterprise HR/Finance/IT with LLM orchestrator |
| `distributed_mesh.yaml` | Distributed | Supply chain mesh with peer negotiation |
| `edge_agent_workflow.yaml` | Centralized (Edge) | Factory floor predictive maintenance on K3s |

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full architecture
reference, including the four-tier hierarchy, ASL syntax, security model,
and CLI reference.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style,
and pull request guidelines.

## License

Apache-2.0 — see [LICENSE](LICENSE).