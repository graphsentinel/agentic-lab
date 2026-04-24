# AGENT-LAB

**Declarative agentic workflow architecture and automated code/container generation.**

AGENT-LAB bridges abstract agentic system design and production-ready deployments through:

1. **Phase 1 — ASL (Agentic Specification Language)**: Define architecture, agent hierarchy, security, and protocols in YAML.
2. **Phase 2 — Code & Container Generation**: Translate ASL specs into framework-specific Python/Go code, Dockerfiles, and Kubernetes manifests.

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Scaffold a new project
agentlab init my-project --template centralized

# Validate an ASL spec
agentlab validate examples/centralized_enterprise.yaml

# Generate code and manifests
agentlab generate examples/centralized_enterprise.yaml --output-dir ./output
```

## Architecture

AGENT-LAB enforces a three-tier hierarchical agent model:

- **Strategic Layer** — Global Orchestrators (LangGraph/LLM-powered planning)
- **Tactical Layer** — Domain Sub-Orchestrators (HR, Finance, etc.)
- **Execution Layer** — Simple Operators (deterministic) and Complex Operators (LLM/ML/GraphRAG)

See [docs/architecture.md](docs/architecture.md) for full details.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

Apache-2.0
