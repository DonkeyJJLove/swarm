# swarm — AI-Native Enterprise Roadmap

Enterprise role: **Distributed Execution Mesh**.

The current repository is a real Kubernetes laboratory with drone workloads, UDP/MQTT telemetry, APIs, PostgreSQL, Istio, Prometheus/Grafana/Jaeger, NetworkPolicy and RBAC. The enterprise direction is to preserve the lab while extracting a generic runtime substrate for Cyber-Lion agents and dynamic swarms.

## Target

```text
AgentSpec / SwarmSpec
        ↓
workload identity
        ↓
scoped capability materialization
        ↓
ExecutionDomain
        ↓
Local Policy Enforcement
        ↓
process / service / tool
        ↓
real effect
        ↓
telemetry + provenance + execution receipt
```

Kubernetes/Istio remain infrastructure. They do not themselves define agent identity or mission authority.

## Phase 1 — secure and normalize the laboratory

- merge the existing `shell=True` / input-sanitization remediation;
- keep one canonical README;
- review RBAC using actual workload needs rather than broad coordinator privileges;
- remove static/example secrets from paths that could be mistaken for production configuration;
- add CI for Python compile, manifest validation and security regressions.

## Phase 2 — generic runtime roles

Extract reusable concepts from drone-specific services:

```text
ExecutionNode
AgentWorkload
SwarmWorkload
TelemetryCollector
CapabilityBrokerClient
LocalPEP
RuntimeLauncher
HealthController
RevokeController
```

Keep drone workloads as an example implementation.

## Phase 3 — AgentSpec/SwarmSpec adapter

Consume versioned Cyber-Lion contracts and bind:

```text
agent_instance_id
mission_id
swarm_id
workload identity
pod/container/process
execution domain
capability lease
correlation_id
```

A model provider name or IP address is never an agent identity.

## Phase 4 — capability leases

An agent receives a time/scope-bounded capability, not ambient cluster authority.

```text
CapabilityLease = {
  agent_instance,
  capability_id,
  resource scope,
  action scope,
  expiry,
  policy/gate refs,
  correlation
}
```

No spawned agent inherits all credentials from its parent.

## Phase 5 — observability-conditioned authority

Required runtime chain:

```text
proposal
→ policy/gate
→ capability lease
→ workload/process
→ resource/tool
→ effect
→ result
```

Node lifecycle:

```text
ACTIVE
→ DEGRADED
→ RESTRICTED
→ QUARANTINED
→ FROZEN
→ REVOKED
```

If required telemetry/provenance disappears, effective authority must decrease rather than only generating an alert.

## Phase 6 — topology reconfiguration

Support dynamic `MosaicDelta` operations:

```text
spawn workload
remove workload
change communication edge
move execution domain
change capability lease
freeze/dissolve swarm
```

Authority-expanding topology deltas require explicit gate evidence.

## Phase 7 — stronger isolation providers

Separate:

```text
bounded local execution
container isolation
Kubernetes namespace isolation
microVM/VM isolation
privileged execution
```

Each provider declares its actual isolation properties; do not call a container or seccomp rule a complete sandbox by assumption.

## Phase 8 — ExecutionReceipt

Every consequential run returns a receipt containing:

```text
execution_id
agent/swarm identity
capability lease
policy/gate refs
runtime identity
input hashes
artifact/image refs
start/end
exit/result
effect summary
telemetry/provenance refs
```

## Security tests

- forged agent identity;
- expired capability lease;
- cross-namespace access;
- unauthorized egress;
- delegation escalation;
- missing gate;
- observability loss;
- kill/revoke behavior;
- command/path injection in diagnostic tooling;
- stale SwarmSpec.

## Do not do

```text
IP == identity
PID == organizational identity
Kubernetes RBAC == mission authority
service mesh == complete Agent Control Mesh
model proposal == executable command
parent credentials == child credentials
```

## Enterprise reference

`https://github.com/DonkeyJJLove/ai_platform/tree/master/cyber_lion/enterprise`
