"""Pure-data qualification of prerequisites for future runtime identity binding.

This module analyzes evidence only. It never creates an agent, runtime identity,
authority grant, executor, credential, or executable effect.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import json
from typing import Optional, Tuple


REFERENCE_REPOSITORY = "DonkeyJJLove/ai_platform"
REFERENCE_COMMIT_SHA = "da4dbd7b27b4833c0debddf839e003f2ce170d5c"
SEMANTIC_MAPPING_STATUS = "SEMANTIC_BRIDGE_REQUIRES_EXPLICIT_ADAPTER"
SWARM_RUNTIME_IDENTITY_SCHEMA_EQ_F009 = False


@dataclass(frozen=True)
class CanonicalIdentitySourceReference:
    repository: str
    commit_sha: str
    contract_path: str
    contract_blob_sha: str
    contract_name: str
    semantic_role: str


CANONICAL_IDENTITY_SOURCES = (
    CanonicalIdentitySourceReference(
        repository=REFERENCE_REPOSITORY,
        commit_sha=REFERENCE_COMMIT_SHA,
        contract_path="cyber_lion/contracts/agent_registry.py",
        contract_blob_sha="c2c9cc38a213d33714776b77730efbbb1e58a1a3",
        contract_name="AgentInstance",
        semantic_role="CANONICAL_ORGANIZATIONAL_INSTANCE_SOURCE_CANDIDATE",
    ),
    CanonicalIdentitySourceReference(
        repository=REFERENCE_REPOSITORY,
        commit_sha=REFERENCE_COMMIT_SHA,
        contract_path="cyber_lion/contracts/runtime_enforcement.py",
        contract_blob_sha="93dee195e5b58a2f1a8efde5487bfb3c99da54ef",
        contract_name="RuntimeIdentityBinding",
        semantic_role="CANONICAL_RUNTIME_EXECUTOR_IDENTITY_REFERENCE",
    ),
    CanonicalIdentitySourceReference(
        repository=REFERENCE_REPOSITORY,
        commit_sha=REFERENCE_COMMIT_SHA,
        contract_path="cyber_lion/contracts/executor_provisioning.py",
        contract_blob_sha="48424616201b1d52bea1f3307672c01ada473c7b",
        contract_name="ExecutorProvisioningRequest",
        semantic_role="CANONICAL_IMMUTABLE_ARTIFACT_PROVENANCE_REFERENCE",
    ),
)


class IdentityPrerequisiteStatus(str, Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"


class MissingIdentityRequirement(str, Enum):
    AGENT_INSTANCE_MISSING = "AGENT_INSTANCE_MISSING"
    AGENT_SPEC_BINDING_MISSING = "AGENT_SPEC_BINDING_MISSING"
    AGENT_INSTANCE_NOT_ACTIVE = "AGENT_INSTANCE_NOT_ACTIVE"
    AGENT_EVIDENCE_MISSING = "AGENT_EVIDENCE_MISSING"
    WORKLOAD_IDENTITY_MISSING = "WORKLOAD_IDENTITY_MISSING"
    IMMUTABLE_ARTIFACT_MISSING = "IMMUTABLE_ARTIFACT_MISSING"
    RUNTIME_INSTANCE_MISSING = "RUNTIME_INSTANCE_MISSING"
    SANDBOX_ID_MISSING = "SANDBOX_ID_MISSING"
    WORKSPACE_ID_MISSING = "WORKSPACE_ID_MISSING"
    RUNTIME_ATTESTATION_MISSING = "RUNTIME_ATTESTATION_MISSING"
    PROVISIONED_EXECUTOR_MISSING = "PROVISIONED_EXECUTOR_MISSING"
    CURRENTNESS_EVIDENCE_MISSING = "CURRENTNESS_EVIDENCE_MISSING"
    SCHEMA_COMPATIBILITY_UNRESOLVED = "SCHEMA_COMPATIBILITY_UNRESOLVED"


@dataclass(frozen=True)
class IdentityPrerequisiteEvidence:
    agent_registry_instance_id: Optional[str] = None
    agent_registry_agent_id: Optional[str] = None
    agent_registry_spec_version: Optional[str] = None
    agent_registry_spec_digest: Optional[str] = None
    agent_registry_state: Optional[str] = None
    agent_registry_generation: Optional[int] = None
    agent_registry_evidence_refs: Tuple[str, ...] = ()
    workload_identity: Optional[str] = None
    immutable_image_digest: Optional[str] = None
    runtime_instance_id: Optional[str] = None
    sandbox_id: Optional[str] = None
    workspace_id: Optional[str] = None
    runtime_attestation_digest: Optional[str] = None
    provisioned_executor_digest: Optional[str] = None
    authority_currentness_evidence: Optional[str] = None
    source_refs: Tuple[CanonicalIdentitySourceReference, ...] = ()
    schema_compatibility_qualified: bool = False


@dataclass(frozen=True)
class IdentityPrerequisiteQualification:
    status: IdentityPrerequisiteStatus
    missing_requirements: Tuple[MissingIdentityRequirement, ...]
    source_reference_digest: str
    evidence_digest: str


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def canonical_source_reference_digest(
    refs: Tuple[CanonicalIdentitySourceReference, ...] = CANONICAL_IDENTITY_SOURCES,
) -> str:
    return _digest_json([asdict(item) for item in refs])


def canonical_evidence_digest(evidence: IdentityPrerequisiteEvidence) -> str:
    return _digest_json(asdict(evidence))


def qualify_identity_prerequisites(
    evidence: IdentityPrerequisiteEvidence,
) -> IdentityPrerequisiteQualification:
    missing = []

    if not _text(evidence.agent_registry_instance_id):
        missing.append(MissingIdentityRequirement.AGENT_INSTANCE_MISSING)

    if not (
        _text(evidence.agent_registry_agent_id)
        and _text(evidence.agent_registry_spec_version)
        and _sha256(evidence.agent_registry_spec_digest)
    ):
        missing.append(MissingIdentityRequirement.AGENT_SPEC_BINDING_MISSING)

    if evidence.agent_registry_state != "ACTIVE":
        missing.append(MissingIdentityRequirement.AGENT_INSTANCE_NOT_ACTIVE)

    if (
        not isinstance(evidence.agent_registry_generation, int)
        or isinstance(evidence.agent_registry_generation, bool)
        or evidence.agent_registry_generation < 0
    ):
        if MissingIdentityRequirement.AGENT_SPEC_BINDING_MISSING not in missing:
            missing.append(MissingIdentityRequirement.AGENT_SPEC_BINDING_MISSING)

    if (
        not isinstance(evidence.agent_registry_evidence_refs, tuple)
        or not evidence.agent_registry_evidence_refs
        or any(not _text(item) for item in evidence.agent_registry_evidence_refs)
    ):
        missing.append(MissingIdentityRequirement.AGENT_EVIDENCE_MISSING)

    if not _text(evidence.workload_identity):
        missing.append(MissingIdentityRequirement.WORKLOAD_IDENTITY_MISSING)
    if not _sha256(evidence.immutable_image_digest):
        missing.append(MissingIdentityRequirement.IMMUTABLE_ARTIFACT_MISSING)
    if not _text(evidence.runtime_instance_id):
        missing.append(MissingIdentityRequirement.RUNTIME_INSTANCE_MISSING)
    if not _text(evidence.sandbox_id):
        missing.append(MissingIdentityRequirement.SANDBOX_ID_MISSING)
    if not _text(evidence.workspace_id):
        missing.append(MissingIdentityRequirement.WORKSPACE_ID_MISSING)
    if not _sha256(evidence.runtime_attestation_digest):
        missing.append(MissingIdentityRequirement.RUNTIME_ATTESTATION_MISSING)
    if not _sha256(evidence.provisioned_executor_digest):
        missing.append(MissingIdentityRequirement.PROVISIONED_EXECUTOR_MISSING)
    if not _text(evidence.authority_currentness_evidence):
        missing.append(MissingIdentityRequirement.CURRENTNESS_EVIDENCE_MISSING)

    if (
        evidence.source_refs != CANONICAL_IDENTITY_SOURCES
        or not evidence.schema_compatibility_qualified
    ):
        missing.append(MissingIdentityRequirement.SCHEMA_COMPATIBILITY_UNRESOLVED)

    missing_requirements = tuple(dict.fromkeys(missing))
    status = (
        IdentityPrerequisiteStatus.READY
        if not missing_requirements
        else IdentityPrerequisiteStatus.NOT_READY
    )
    return IdentityPrerequisiteQualification(
        status=status,
        missing_requirements=missing_requirements,
        source_reference_digest=canonical_source_reference_digest(evidence.source_refs),
        evidence_digest=canonical_evidence_digest(evidence),
    )
