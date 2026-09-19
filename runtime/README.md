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

## Runtime identity prerequisites

Identity prerequisite qualification is evidence analysis only. It does not
materialize `RuntimeIdentityBinding`, create an agent, or grant authority.

The current compatibility bridge pins three canonical Cyber-Lion contracts at
`DonkeyJJLove/ai_platform@da4dbd7b27b4833c0debddf839e003f2ce170d5c`:

- organizational identity: Agent Registry `AgentInstance.instance_id`, bound to
  agent/spec/lifecycle/evidence state;
- runtime/executor identity: F009 runtime identity plus provisioned executor and
  runtime attestation evidence;
- artifact identity: immutable SHA-256 `ExecutorProvisioningRequest.image_digest`.

The SWARM roadmap term `agent_instance_id` is not silently renamed into the
Cyber-Lion field. Its relationship to `AgentInstance.instance_id` is recorded
as `SEMANTIC_BRIDGE_REQUIRES_EXPLICIT_ADAPTER`.

The local SWARM `RuntimeIdentityBinding` schema and the canonical F009 schema
are not equivalent. No positional mapping, name-only mapping, or adapter is
implemented by this phase.

The current drone example remains `NOT_READY`: no canonical AgentInstance
evidence, immutable image digest, runtime instance, runtime attestation,
provisioned-executor digest, or qualified schema compatibility is fabricated.

The invariants are:

```text
ORGANIZATIONAL_IDENTITY
+
ARTIFACT_PROVENANCE
+
RUNTIME_ATTESTATION
!=
AUTHORITY
```

and:

```text
PREREQUISITES_READY
!=
RUNTIME_IDENTITY_BOUND
```
