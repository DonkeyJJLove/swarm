"""Descriptive AgentWorkload example for the current drone laboratory workload.

This module is pure data. It does not materialize agent identity, runtime identity,
mission authority, admission evidence, or an executable effect.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from runtime.contracts import RuntimeRole


@dataclass(frozen=True)
class SourceEvidence:
    path: str
    blob_sha: str


@dataclass(frozen=True)
class AgentWorkloadExampleDescriptor:
    example_id: str
    runtime_role: RuntimeRole
    source_master_sha: str
    source_evidence: Tuple[SourceEvidence, ...]
    workload_kind: str
    namespace: str
    workload_name: str
    declared_replicas: int
    pod_label_selector: str
    container_name: str
    image_reference: str
    artifact_identity_status: str
    runtime_identifier_source: str
    runtime_identifier_classification: str
    agent_identity_status: str
    runtime_identity_status: str
    service_account_binding_status: str
    manifest_declared_ports: Tuple[str, ...]
    observed_application_channels: Tuple[str, ...]
    declared_but_unobserved_configuration: Tuple[str, ...]
    network_policy_binding_status: str
    authority_status: str


DRONE_AGENT_WORKLOAD_EXAMPLE = AgentWorkloadExampleDescriptor(
    example_id="drone-workload-descriptive-example-v1",
    runtime_role=RuntimeRole.AGENT_WORKLOAD,
    source_master_sha="7301c815127b52b8f40858a54f3fe8e905798312",
    source_evidence=(
        SourceEvidence("drones/drone_logic.py", "96c3544d07804c770284521fbac2030d71a72d3d"),
        SourceEvidence("drones/drone-deployment.yaml", "1d291aa0d29d2e40a180997dbcb5d4616e9ccaca"),
        SourceEvidence("drones/drone-service.yaml", "338a0a0e2bca0f56b69b7cd4f8aaabfb1016349f"),
        SourceEvidence("drones/Dockerfile", "a022830350bdbfe03e2070d633da28a27b6cec23"),
        SourceEvidence("security/policies/network-policy.yaml", "4a99a5a1409495b4a8e6ea156af4211a38222d47"),
    ),
    workload_kind="Deployment",
    namespace="laboratory-swarm",
    workload_name="drone",
    declared_replicas=10,
    pod_label_selector="app=drone",
    container_name="drone",
    image_reference="localhost:5000/drone:latest",
    artifact_identity_status="UNRESOLVED_MUTABLE_TAG",
    runtime_identifier_source="metadata.name",
    runtime_identifier_classification="INFRASTRUCTURE_RUNTIME_IDENTIFIER",
    agent_identity_status="UNBOUND",
    runtime_identity_status="NOT_MATERIALIZED",
    service_account_binding_status="ABSENT",
    manifest_declared_ports=("TCP/7000",),
    observed_application_channels=(
        "UDP -> aggregator-service.laboratory-swarm.svc.cluster.local:6000",
    ),
    declared_but_unobserved_configuration=("MQTT_BROKER", "MQTT_PORT"),
    network_policy_binding_status="NO_DRONE_SELECTOR_OBSERVED",
    authority_status="NONE",
)
