# Agent Card

> **`[IMPLEMENTED]`** — Agent Card models are shipped in the current release (`security/agent_card.py`).

An **Agent Card** is an identity specification for each agent in the system, analogous to a
digital certificate. It solves the **identity masking problem**: in most multi-agent systems,
multiple agents share API keys or credentials, making per-agent accountability impossible.

---

## What an Agent Card Declares

| Field | Description |
|-------|-------------|
| `name` | Human-readable agent name |
| `id` | Unique identifier (UUID or DID) |
| `role` | Functional role within the hierarchy |
| `layer` | `strategic` / `tactical` / `execution` |
| `clearance_level` | Trust tier: `low` / `medium` / `high` / `critical` |
| `reasoning_type` | `llm` / `deterministic` / `predictive` / `graphrag` |
| `tool_permissions` | Scoped tool access (from ASL `ToolBinding`) |
| `communication_protocols` | Declared communication endpoints |
| `scope` | Operational boundary within which behavior is normal |

---

## Example

```yaml
agent_card:
  name: secure_db_query
  id: "urn:agent:graphsentinel:hr-system:secure-db-query"
  layer: execution
  role: Simple Operator
  clearance_level: medium
  reasoning_type: deterministic
  tool_permissions:
    - tool: postgres_hr_db
      operations: [read]
  communication_protocols:
    - type: a2a
      transport: grpc
      auth: spiffe-mtls
      endpoint: "grpc://hr-agents.internal:50051"
  scope:
    allowed_tool_types: [database]
    allowed_operations: [read]
    max_delegation_depth: 0         # execution layer; cannot delegate further
```

---

## Clearance Levels

Clearance levels control access to sensitive operations and data:

| Level | Description | Typical Use |
|-------|-------------|-------------|
| `low` | Default; public or non-sensitive operations | Web search, public APIs |
| `medium` | Business data access | Internal databases, HR records |
| `high` | Sensitive or regulated data | Financial records, PII |
| `critical` | Highest sensitivity; requires deterministic reasoning | Compliance decisions, financial transactions |

An agent with `clearance_level: critical` is **required** to have `reasoning_type: deterministic`
to prevent stochastic hallucination on high-stakes decisions.

---

## Reasoning Types

| Type | Description | Hallucination Risk |
|------|-------------|-------------------|
| `llm` | LLM-powered; planning, generation, analysis | Present |
| `deterministic` | Rule-based; predictable, auditable | Zero |
| `predictive` | ML/DL inference (ONNX, GGUF, TFLite) | Model-bounded |
| `graphrag` | Graph-enhanced retrieval-augmented generation | Low |

---

## OTel Attribution

Every OpenTelemetry span emitted by the governance layer carries the Agent Card `id`
as an attribute. This enables:

- Per-agent filtering in your observability platform
- Per-agent cost attribution (token usage, API calls)
- Per-agent audit trails in compliance reports

```
gen_ai.agent.id          = "urn:agent:graphsentinel:hr-system:secure-db-query"
gen_ai.agent.role        = "Simple Operator"
gen_ai.agent.layer       = "execution"
gen_ai.agent.clearance   = "medium"
gen_ai.policy.rule       = "scope_monotonicity"
gen_ai.policy.verdict    = "block"
```

---

## Relationship to A2A Authentication

The Agent Card is complementary to — not a replacement for — A2A authentication:

| A2A | Agent Card |
|-----|------------|
| Authenticates *which* agent is calling | Declares *what* the agent is allowed to do |
| Protocol-level (gRPC + mTLS, DID) | Application-level (ASL + governance layer) |
| Peer-to-peer identity | System-wide accountability |

Together they provide both **authentication** (is this agent who it claims to be?)
and **authorization** (is this agent allowed to perform this action?).

---

## See Also

- [Authorization](authorization.md) — tool-binding authorization model
- [Governance Contract](governance-contract.md) — contract lifecycle
- [Taxonomy → Communication Protocols](../taxonomy/communication-protocols.md) — A2A protocol
- [Architecture → Security Model](../architecture.md#security-model)
