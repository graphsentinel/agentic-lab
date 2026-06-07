# Governance Implications

> **`[PILOT-VALIDATED]`** — Collaborative governance is validated. Adversarial and mixed-pattern governance are `[IN DEVELOPMENT]`.

This page describes how collaborative and adversarial pattern classes affect governance design
and enforcement strategy.

---

## Summary Table

| Pattern Type | Governance Challenge | MABaC Response |
|-------------|---------------------|----------------|
| Collaborative | Scope creep through delegation chains | Scope monotonicity enforcement |
| Collaborative | Silent failures in pipeline stages | Per-stage behavioral envelopes |
| Adversarial | Agent manipulation or co-option | Immutable governance contracts |
| Adversarial | Byzantine behavior detection | Graph-level anomaly scoring |
| Mixed | Trust boundary enforcement | Agent Cards + cross-framework mesh |

---

## Collaborative Pattern Implications

### Scope Creep Through Delegation Chains

In a long delegation chain, each intermediate agent can introduce a small scope expansion
that compounds over the chain length:

```
Orchestrator (scope: A, B, C)
    → Sub-Orch (scope: A, B)        ← should be subset
        → Operator (scope: A, B, D) ← VIOLATION: D not in sub-orch scope
```

**MABaC response**: Scope monotonicity is enforced at *every* delegation edge, not just
at the entry point. Each edge is independently validated.

### Silent Failures in Pipeline Stages

A pipeline agent that receives bad input may pass bad output downstream without raising an
error. By the time the failure is detected, multiple downstream agents have been affected.

```
[Stage A] → bad_output → [Stage B] → propagated_error → [Stage C] → corrupted_result
```

**MABaC response**: Per-stage behavioral envelopes validate output schemas and detect
unexpected output distributions before they propagate. Each stage has its own deviation
score and enforcement threshold.

### Aggregator Integrity

In ensemble patterns, the aggregator is a single point of failure. Even if all input
agents are correct, a compromised aggregator can produce incorrect consensus.

**MABaC response**: The aggregator is itself governed by a behavioral envelope. Its
expected behavior (aggregation strategy, output schema, confidence range) is declared
in MABaC and enforced at the aggregation step.

---

## Adversarial Pattern Implications

### Agent Manipulation and Co-option

In adversarial scenarios, a malicious agent may attempt to co-opt a governance agent
(e.g., the Critic in adversarial validation) by:
- Injecting content into the Critic's context that biases its judgment
- Exploiting shared infrastructure (same model, same API key) to influence the Critic
- Social engineering via generated content designed to manipulate LLM-based reviewers

**MABaC response**: Immutable governance contracts (version-controlled, signed) ensure
that the Critic's behavioral constraints cannot be modified at runtime. Agent Cards with
separate identities enforce independence between Generator and Critic.

!!! warning "Prompt Injection"
    Adversarial agents may embed prompt injection content in their outputs, targeting
    LLM-based Critic or Monitor agents. Behavioral envelopes that score output schemas
    (not just tool selections) provide a mitigation layer.

### Byzantine Behavior Detection

A Byzantine agent may behave correctly most of the time but deviate at critical moments.
Point-in-time rule checks are insufficient — the governance layer needs to detect
*patterns* of behavior, not just individual violations.

**MABaC response**: Graph-level anomaly scoring tracks the *sequence* of an agent's
decisions over time (not just individual tool calls). Unexpected behavioral sequences
— even if each individual call is within scope — trigger a deviation alert.

---

## Mixed-Pattern Implications

Real deployments combine collaborative and adversarial elements (e.g., a collaborative
pipeline with an adversarial validation step, or a competitive bidding system within a
collaborative task-decomposition hierarchy).

### Trust Boundary Enforcement

When collaborative agents delegate to agents in different frameworks, trust boundaries
must be enforced explicitly:

```
Framework A (collaborative, trusted) → [A2A Proxy] → Framework B (untrusted / adversarial)
                                             ↓
                                   Agent Card verification
                                   Scope monotonicity check
                                   Behavioral envelope active
```

**MABaC response**: Agent Cards provide per-agent identity even across framework boundaries.
The A2A proxy enforces the governance contract at the trust boundary, regardless of what
the source framework claims about the agent's identity.

---

## Governance Contract Design Principles

| Principle | Description |
|-----------|-------------|
| **Least privilege** | Declare the minimum scope required, not the maximum convenient |
| **Independent enforcement** | Each layer's envelope is independent; a failure in one does not disable others |
| **Auditable attribution** | Every gate decision is attributed to a specific Agent Card and contract version |
| **Graceful degradation** | When the governance core is unavailable, fail closed (block) not open |
| **Immutability at runtime** | Governance contracts cannot be modified by agents at runtime |

---

## See Also

- [Collaborative Patterns](collaborative.md)
- [Adversarial Patterns](adversarial.md)
- [Concepts → Behavioral Envelope](../concepts/behavioral-envelope.md)
- [Concepts → Governance Contract](../concepts/governance-contract.md)
