# Gossip, DHT & Consensus

> **`[RESEARCH]`** — Decentralized protocol research. Not currently implemented.

This page documents decentralized protocol research directions for distributed and federated
multi-agent governance. These protocols become relevant when agents span multiple clusters,
organizations, or operate with intermittent connectivity.

---

## Why Decentralized Protocols?

The [pyramid topology](../topologies/pyramid.md) relies on a central orchestrator and assumes
reliable connectivity. In distributed edge or federated scenarios:

- There may be **no reliable central authority** (multi-organization deployments)
- Agents may **operate offline** for extended periods (edge / IoT)
- **Trust must be established without a central identity provider**
- Governance state (policy updates, baselines, alerts) must **propagate without a central broker**

---

## Gossip Protocols

### What They Do

Gossip protocols propagate information across a distributed network without central coordination.
Each node periodically shares its state with a random subset of peers; information spreads
exponentially until all nodes converge.

### Application to Agent Governance

| Governance State | Gossip Use |
|-----------------|-----------|
| Policy updates | New governance contract versions propagate to all agents without a central push |
| Baseline snapshots | Behavioral baselines are shared across agent clusters for cross-site consistency |
| Anomaly alerts | A detected breach propagates rapidly across the mesh without a central coordinator |
| Agent Card revocations | Compromised agent identities are revoked across the entire estate |

### Properties

- **Eventual consistency** — all nodes converge to the same state, but not simultaneously
- **Partition tolerant** — gossip continues across network partitions; state merges when connectivity resumes
- **Scalable** — O(log N) rounds to reach full propagation; scales to thousands of agents

### Open Questions

- What is the acceptable **convergence latency** for governance policy updates? (A critical rule block must propagate faster than a baseline update)
- How do **conflicting policies** (from different gossip sources) get resolved?
- Can gossip be used for **baseline aggregation** without revealing sensitive behavioral data?

---

## Distributed Hash Tables (DHTs)

### What They Do

A DHT provides decentralized key-value storage where each node is responsible for a subset
of the keyspace. Lookups route through the network in O(log N) hops without a central registry.

### Application to Agent Governance

**Capability Discovery** — In a mesh topology, agents announce their capabilities to the DHT:

```
Agent B announces:
  key:   "capability:route_planning"
  value: {agent_id: "urn:agent:...", endpoint: "grpc://...", scope: {...}}

Agent A queries:
  key:   "capability:route_planning"
  → finds Agent B
  → establishes A2A connection
```

**Governance Contract Registry** — Governance contracts can be stored in the DHT and
referenced by content hash (CID), enabling:
- Content-addressed, tamper-evident contract storage
- Peers can verify the contract they received matches what was published
- No single point of failure for the contract registry

### Open Questions

- Which DHT protocol is most appropriate? (Kademlia, Chord, libp2p)
- How do DHT nodes handle **byzantine peers** that advertise false capabilities?
- What is the right **TTL policy** for capability announcements?

---

## Consensus-Driven Message Routing

### What They Do

Byzantine fault-tolerant (BFT) consensus ensures that a group of agents reaches a
**valid collective decision** even when some members are compromised or misbehaving.

For `N` agents with `f` Byzantine faults: BFT requires `N ≥ 3f + 1`.

### Application to Agent Governance

**Conflict Resolution** — When competing agents produce contradictory results:
```
Agent A: result = "approve"
Agent B: result = "reject"
Agent C: result = "approve"
→ BFT consensus (N=3, f=1): "approve" (2/3 agree, within BFT tolerance)
```

**High-Stakes Decisions** — For irreversible actions (financial transactions, config changes),
require BFT consensus across multiple independent agents before execution.

**Byzantine Agent Detection** — An agent that consistently deviates from the consensus
decision is a candidate for Byzantine classification and governance quarantine.

### BFT Protocols

| Protocol | Latency | Throughput | Notes |
|---------|---------|-----------|-------|
| PBFT | O(N²) messages | Moderate | Classic; high message complexity |
| HotStuff | O(N) messages | High | Used in many modern BFT systems |
| Tendermint | O(N) messages | High | Widely deployed in blockchain contexts |

### Open Questions

- What is the **latency budget** for BFT consensus in a governance gate? (Sub-second is likely required)
- How do BFT mechanisms **compose** with existing A2A authentication?
- At what **agent count** does BFT overhead become impractical for real-time governance?

---

## Research Roadmap

```mermaid
gantt
    title Decentralized Protocol Research Roadmap
    dateFormat  YYYY-Q
    section Gossip
    Policy propagation design       :2026-Q3, 2026-Q4
    Prototype implementation        :2026-Q4, 2027-Q1
    section DHT
    Capability discovery design     :2026-Q3, 2026-Q4
    libp2p integration prototype    :2027-Q1, 2027-Q2
    section BFT Consensus
    Protocol selection and design   :2026-Q4, 2027-Q1
    Integration with A2A            :2027-Q1, 2027-Q2
```

---

## See Also

- [Topologies → Mesh](../topologies/mesh.md) — primary consumer of these protocols
- [Vision → Federation](federation.md) — cross-org governance context
- [Taxonomy → Communication Protocols](../taxonomy/communication-protocols.md) — current protocol landscape
