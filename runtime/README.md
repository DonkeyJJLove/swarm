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

## AgentWorkload descriptive example

`runtime/examples/drone_agent_workload.py` is the first descriptive mapping of
an existing laboratory workload to the `AgentWorkload` architectural role. It
does not create an `AgentSpec`, `RuntimeIdentityBinding`, admission request,
capability lease, or executable authority.

The current drone Deployment is recorded as infrastructure evidence only. Its
`DRONE_ID` is derived from Kubernetes `metadata.name`; that value is an
infrastructure runtime identifier and is not an `agent_instance_id`. The image
reference is `localhost:5000/drone:latest`, so the artifact identity remains
`UNRESOLVED_MUTABLE_TAG` rather than being promoted to an artifact digest.

The example also keeps declared infrastructure separate from observed
application behavior. `MQTT_BROKER` and `MQTT_PORT` are declared by the
Deployment but are not used by the current `drone_logic.py`. TCP/7000 is
declared in the Deployment and Service, while the current Python workload does
not bind or listen on port 7000. The current repository NetworkPolicy selects
`app=aggregator`, not `app=drone`, so it is not treated as a drone workload
policy.

The descriptor grants no authority and executes no runtime. Its invariant is:

```text
DESCRIBED_AS_AGENTWORKLOAD
!=
AUTHORIZED_AS_AGENT
```
