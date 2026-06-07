# Pyramid — Centralized Hierarchy

> **`[IMPLEMENTED]`** — Template A is the v1 target; delegation edges and scope are fully implemented.

The **Pyramid** (or Centralized Hierarchy) topology is the primary architectural template in
agentic-lab v1. It implements top-down delegation, bottom-up reporting, and clear authority
lines between layers.

---

## Structure

```
              Orchestrator
             /            \
      Sub-Orch A      Sub-Orch B
      /    \              /    \
   Op1    Op2          Op3    Op4
```

- Delegation flows **downward** — Orchestrator → Sub-Orchestrators → Operators
- Reporting flows **upward** — Operators → Sub-Orchestrators → Orchestrator
- Each layer has a **bounded scope** — a sub-orchestrator cannot exceed the orchestrator's permissions

---

## When to Use Pyramid

| Signal | Pyramid is a Good Fit |
|--------|----------------------|
| Enterprise workflow with established governance | ✓ |
| Compliance requirements (SOX, HIPAA, GDPR) | ✓ |
| Multi-department coordination (HR, Finance, IT) | ✓ |
| Clear ownership and authority lines required | ✓ |
| Auditable delegation chain needed | ✓ |
| Self-organizing, decentralized agents | ✗ (use Mesh) |
| Intermittent connectivity / edge-only | ✗ (use Mesh) |

---

## ASL Declaration

```yaml
spec:
  architecture_template: centralized
  target_deployment: kubernetes
```

---

## Enterprise Example

The `centralized_enterprise.yaml` example implements a three-domain pyramid:

```
global_orchestrator  (Strategic)
├── hr_sub_orchestrator  (Tactical)
│   ├── secure_db_query         (Execution — Simple)
│   └── hr_report_generator     (Execution — Complex)
├── finance_sub_orchestrator  (Tactical)
│   ├── financial_analyst       (Execution — Complex)
│   └── budget_query            (Execution — Simple)
└── it_sub_orchestrator  (Tactical)
    ├── infra_monitor           (Execution — Simple)
    └── incident_responder      (Execution — Complex)
```

See the [full example](../reference/examples.md#centralized-enterprise) for the complete YAML.

---

## Governance Properties

**Scope monotonicity** is strictly enforced in the pyramid:

- The `global_orchestrator` declares its tool bindings with full permissions.
- Each `sub_orchestrator` receives a **subset** of those permissions.
- Each `operator` receives a **subset** of its sub-orchestrator's permissions.

This creates a mathematically verifiable permission lattice — any tool call at the execution
layer is guaranteed to be within the scope originally granted at the strategic layer.

---

## Drift Patterns

The pyramid topology produces crisp, demo-able behavioral drift patterns for governance:

| Pattern | Description |
|---------|-------------|
| Operator bypasses sub-orchestrator | Execution-layer agent calls strategic-layer tools directly |
| Sub-orchestrator scope creep | Tactical agent calls tools outside its declared domain |
| Unauthorized lateral communication | Sub-orchestrators coordinate without ASL declaration |
| Skip-level delegation | Orchestrator delegates directly to an operator (bypassing tactical layer) |

Each pattern is detectable by the [Behavioral Envelope](../concepts/behavioral-envelope.md)
and produces a policy-attributed OTel span.

---

## See Also

- [Mesh (Distributed)](mesh.md) — the alternative topology
- [Deployment Targets](deployment-targets.md) — where to deploy a pyramid
- [Examples → Centralized Enterprise](../reference/examples.md#centralized-enterprise)
- [Taxonomy → Interaction Patterns](../taxonomy/interaction-patterns.md)
