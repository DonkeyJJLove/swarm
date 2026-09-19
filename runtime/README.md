# Runtime admission contracts

This directory is the contract-only entry into SWARM Phase 2 generic runtime roles.

The role names (`ExecutionNode`, `AgentWorkload`, `SwarmWorkload`,
`TelemetryCollector`, `CapabilityBrokerClient`, `LocalPEP`, `RuntimeLauncher`,
`HealthController`, `RevokeController`) are architectural labels. They do not
grant process, network, Kubernetes, shell, Docker, capability, or runtime
authority.

The admission boundary is:

```text
PDPResult(ALLOW)
+ RequestedRuntimeEffect
+ RuntimeIdentityBinding
+ explicit authority/currentness evidence
→ RuntimeAdmissionDecision
```

`RuntimeAdmission` is deterministic validation only. It does not execute an
effect, create a process, contact a host, talk to Kubernetes, contact Docker,
or mutate authority.

The central invariant is:

```text
ADMIT != Effect
```

An `ADMIT` result confirms that the requested effect is exactly bounded by the
already-resolved PDP evidence: action digest, runtime identity, currentness,
nonce/replay status, resource scope, action scope, and capabilities. Any
ambiguity or widening denies admission.

Not implemented in this phase:

- `RuntimeLauncher` execution;
- `LocalPEP` effect enforcement;
- capability lease issuance;
- `ExecutionReceipt`;
- persistent replay storage.

The existing drone workloads remain the current domain-specific laboratory
example. This package does not convert them into authoritative generic agent
workloads.
