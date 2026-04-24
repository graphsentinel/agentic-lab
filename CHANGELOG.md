# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-XX-XX

### Added
- Agent Specification Language (ASL) YAML schema with Pydantic models
- Four-tier agent hierarchy: Tools, Strategic, Tactical, Execution
- Shared tools catalogue with per-agent permission narrowing (ToolBinding)
- Agent Card security model with clearance levels and reasoning types
- Edge sync configuration (OCI pull, S3 sync, gRPC stream, MQTT)
- Model artifacts (ONNX, GGUF, TorchScript, TFLite, SafeTensors)
- Workflow artifacts for hot-reload orchestrator graphs
- Code generators: LangChain/LangGraph Python, Native Python
- Generator registry with adapter pattern
- Protocol models: A2A (gRPC+mTLS), MCP (sandboxed sidecar), CloudEvents
- Security governance: PII scrubbing, audit retention, deterministic fallback
- CLI: `agentlab init`, `agentlab validate`, `agentlab generate`
- Three example ASL specs: centralized enterprise, distributed mesh, edge agent