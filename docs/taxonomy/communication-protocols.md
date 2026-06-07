# Communication Protocols

> **`[IMPLEMENTED]`** — MCP, A2A, and CloudEvents models are shipped. OTel `gen_ai.*` semantic conventions are integrated. Future protocols are `[RESEARCH]`.

This page describes the communication protocols in the agentic-lab ecosystem and where each
fits in the governance architecture.

---

## Current Protocol Landscape

| Protocol | Standardizes | Leaves Unaddressed |
|---------|------------|-------------------|
| **MCP** | Tool discovery and invocation | Behavioral governance of tool selections |
| **A2A** | Agent-to-agent authentication and peer collaboration | Authorization (what agents do once connected) |
| **CloudEvents** | Event schema and transport | Agent-specific semantics and governance |
| **OTel (`gen_ai.*`)** | Telemetry schema for LLM/agent observations | Behavioral baseline and deviation scoring |

---

## MCP — Model Context Protocol

**Role**: Standardizes how agents discover and invoke tools.

**In agentic-lab**: Tools declared with `framework: mcp` in the ASL tool catalogue are generated
as MCP-compatible tool stubs. The MCP sidecar runs in a sandboxed container, enforcing network
isolation for tool calls.

```yaml
tools:
  - name: postgres_hr_db
    framework: mcp
    sandboxed: true      # runs in isolated sidecar container
```

**What MCP does not cover**: Once an agent has discovered a tool via MCP, MCP has no say in
*which* tool the agent selects, *how often*, or in *what order*. This is the behavioral
governance gap that [MABaC](../concepts/mabac.md) fills.

---

## A2A — Agent-to-Agent Protocol

**Role**: Standardizes agent-to-agent authentication and peer collaboration using gRPC + mTLS
(for trusted environments) or Decentralized Identifiers (DIDs) for distributed/edge scenarios.

**In agentic-lab**: A2A is the transport for delegation and reporting between agents. Every
delegation edge in the ASL spec corresponds to an A2A connection.

```yaml
protocols:
  internal_a2a:
    transport: grpc
    auth: spiffe-mtls     # K8s workload identity
    # or:
    # auth: did           # Decentralized Identifiers for distributed trust
```

**What A2A does not cover**: A2A authenticates *which* agent is calling. It does not govern
*what* the agent does once connected — that is the domain of [ASL authorization](../concepts/authorization.md).

---

## CloudEvents

**Role**: Standardizes event schema and transport for asynchronous agent communication.

**In agentic-lab**: Used as the event bus for monitoring broadcasts, escalation notifications,
and cross-agent coordination that does not require a synchronous A2A call.

```yaml
protocols:
  event_bus: cloudevents
```

**Example event** (monitor alert):

```json
{
  "specversion": "1.0",
  "type": "agent.monitor.alert.deviation",
  "source": "urn:agent:graphsentinel:hr-system:monitor",
  "subject": "urn:agent:graphsentinel:hr-system:secure-db-query",
  "data": {
    "rule": "allowed_tools_only",
    "verdict": "block",
    "deviation_score": 0.95
  }
}
```

---

## OpenTelemetry — `gen_ai.*` Semantic Conventions

**Role**: Standardizes telemetry schema for LLM and agent observations.

**In agentic-lab**: Every governance gate decision emits a `gen_ai.agent.*` OTel span with
policy attribution. This creates the queryable, auditable trail that replaces opaque logging.

**Key span attributes**:

| Attribute | Example Value |
|-----------|---------------|
| `gen_ai.agent.id` | `"urn:agent:graphsentinel:hr-system:secure-db-query"` |
| `gen_ai.agent.role` | `"Simple Operator"` |
| `gen_ai.agent.layer` | `"execution"` |
| `gen_ai.policy.rule` | `"scope_monotonicity"` |
| `gen_ai.policy.verdict` | `"block"` |
| `gen_ai.policy.contract_version` | `"v1.2.3"` |
| `gen_ai.tool.name` | `"postgres_hr_db"` |
| `gen_ai.tool.operation` | `"write"` |

**What OTel does not (yet) cover**: Behavioral baseline computation and deviation scoring are
not in the current `gen_ai.*` semantic conventions. agentic-lab's contribution is the
declared-vs-actual delta encoded in these spans.

---

## Future Protocol Directions

!!! note "Research"
    The following protocols are relevant to decentralized and federated multi-agent governance.
    They are documented here as research directions, not current implementations.
    See [Vision → Gossip, DHT & Consensus](../vision/gossip-dht-consensus.md).

### Gossip Protocols

For propagating governance state (policy updates, baseline snapshots, anomaly alerts) across
distributed agent networks without central coordination. Relevant when agents span multiple
clusters or organizational boundaries.

### Distributed Hash Tables (DHTs)

For decentralized service discovery and capability registration in mesh topologies. An agent
announces its capabilities and scope to the DHT; peers discover collaborators by querying
capability keys rather than consulting a central registry.

### Consensus-Driven Message Routing

For multi-agent decisions that require agreement (e.g., conflict resolution in adversarial
or competitive scenarios). Byzantine fault-tolerant consensus mechanisms ensure valid
collective decisions even when some agents are compromised or misbehaving.

---

## See Also

- [Governance Levels](governance-levels.md) — where each protocol is enforced
- [Concepts → Authorization](../concepts/authorization.md) — what A2A leaves unaddressed
- [Concepts → Agent Card](../concepts/agent-card.md) — identity in A2A
- [Vision → Framework-Agnostic Core](../vision/framework-agnostic.md)
