# Swarm Process Guard

`swarm` is audited as a distributed execution system. Local component health is necessary but not sufficient; the important object is the **cross-service trajectory**.

## Core path

```text
drone / producer
→ transport (UDP/MQTT)
→ aggregator
→ API / storage
→ AI service / decision
→ server / user-visible effect
```

## Invariants

- identity and authority are not inferred from network location alone;
- telemetry loss must reduce confidence, not silently preserve authority;
- NetworkPolicy / RBAC / Istio policy changes are consequential deltas;
- retries, queues and circuit breakers are tested for cascade amplification;
- AI output must cross an independent application/runtime gate before critical effect;
- each critical event should be reconstructable through logs/traces.

## `_neuro` / EEG-like system state

```text
baseline = stable service graph and telemetry profile
burst    = traffic / retry / event spike
coupling = synchronized change across services
 drift   = behavior no longer explained by config and service contracts
recovery = bounded return to observable stable state
```

## Review loop

```text
service-map baseline
→ configuration / code delta
→ trust-boundary analysis
→ failure injection
→ observability check
→ containment check
→ patch
→ regression
→ merge
```

High-risk review targets: RBAC, NetworkPolicy, Istio gateways/routes, secrets, database access, AI-service authority and retry/circuit-breaker behavior.
