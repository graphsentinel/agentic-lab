# Mesh — Distributed Peer-to-Peer

> **`[RESEARCH]`** — Template B is on the roadmap. The same graph baseline and gate apply, but peer negotiation and contract verification are added scope.

The **Mesh** topology is a distributed, peer-to-peer architecture where agents self-organize
based on capability and task similarity. Authority is contract-negotiated rather than
hierarchically assigned.

---

## Structure

```
   [Agent A] ←—————————→ [Agent B]
       ↑  \               /  ↑
       |   \             /   |
       |    → [Agent C] ←    |
       |       ↑     ↓       |
       └——→ [Agent D] ←——————┘
```

No fixed hierarchy. Each agent declares its capabilities and scope; peers discover
collaborators by querying the capability registry.

---

## When to Use Mesh

| Signal | Mesh is a Good Fit |
|--------|-------------------|
| Decentralized, edge, or federated scenarios | ✓ |
| Agents span multiple organizational boundaries | ✓ |
| Intermittent connectivity (IoT / edge) | ✓ |
| Self-organizing agent clusters by latency/capability | ✓ |
| No single point of authority or control | ✓ |
| Enterprise with established governance hierarchy | ✗ (use Pyramid) |
| Compliance requires clear delegation chain | ✗ (use Pyramid) |

---

## ASL Declaration

```yaml
spec:
  architecture_template: distributed
  target_deployment: edge
```

---

## Supply Chain Example

The `distributed_mesh.yaml` example implements a supply chain mesh:

```yaml
metadata:
  name: supply-chain-mesh

spec:
  architecture_template: distributed
  target_deployment: edge
  protocols:
    internal_a2a:
      transport: grpc
      auth: did            # Decentralized Identifiers for distributed trust
```

Agents in the supply chain mesh negotiate task authority via capability contracts rather
than receiving it through a delegation hierarchy. Each agent announces what it can do;
peers discover collaborators by querying capability keys.

See the [full example](../reference/examples.md#distributed-mesh) for the complete YAML.

---

## Capability Discovery

In a mesh topology, agents register their capabilities with a distributed capability
registry (research: DHT-based). Peers query the registry to find suitable collaborators:

```
Agent A needs: route_planning
    → query capability registry
    → finds Agent B (declares: route_planning_api)
    → negotiates contract (scope, permissions)
    → establishes A2A connection with DID auth
```

---

## Contract Negotiation

Unlike the pyramid where authority flows from a central orchestrator, mesh agents
negotiate authority contracts peer-to-peer:

1. Agent A announces a task and its scope.
2. Agent B responds with its capability declaration and proposed scope.
3. A contract is established only if Agent B's proposed scope is within Agent A's scope.
4. The governance layer validates the contract against both agents' ASL declarations.

---

## Governance Challenges

The mesh topology introduces additional governance complexity compared to the pyramid:

| Challenge | Description | MABaC Response |
|-----------|-------------|---------------|
| No fixed delegation chain | Authority is negotiated, not granted | Contract-level scope verification |
| Dynamic topology | Agent membership changes at runtime | DHT-based capability registry |
| Byzantine agents | Some agents may be compromised | Consensus-based decision gates |
| Scope creep through negotiation | Agents may negotiate excessive scope | Scope monotonicity on contracts |

!!! note "Research"
    Peer negotiation, DHT-based discovery, and Byzantine fault-tolerant consensus are
    active research areas. See [Vision → Gossip, DHT & Consensus](../vision/gossip-dht-consensus.md).

---

## See Also

- [Pyramid (Centralized)](pyramid.md) — the production-ready alternative
- [Examples → Distributed Mesh](../reference/examples.md#distributed-mesh)
- [Vision → Gossip, DHT & Consensus](../vision/gossip-dht-consensus.md)
- [Vision → Federation](../vision/federation.md)
