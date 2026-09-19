"""Pure-data contracts for the SWARM Phase 2 runtime admission boundary."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import FrozenSet, Tuple


class RuntimeRole(str, Enum):
    EXECUTION_NODE = "execution_node"
    AGENT_WORKLOAD = "agent_workload"
    SWARM_WORKLOAD = "swarm_workload"
    TELEMETRY_COLLECTOR = "telemetry_collector"
    CAPABILITY_BROKER_CLIENT = "capability_broker_client"
    LOCAL_PEP = "local_pep"
    RUNTIME_LAUNCHER = "runtime_launcher"
    HEALTH_CONTROLLER = "health_controller"
    REVOKE_CONTROLLER = "revoke_controller"


class PDPDecision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class AdmissionDecision(str, Enum):
    ADMIT = "ADMIT"
    DENY = "DENY"


class AdmissionReason(str, Enum):
    ADMITTED = "ADMITTED"
    PDP_NOT_ALLOW = "PDP_NOT_ALLOW"
    ACTION_DIGEST_MISMATCH = "ACTION_DIGEST_MISMATCH"
    RUNTIME_IDENTITY_MISMATCH = "RUNTIME_IDENTITY_MISMATCH"
    CURRENTNESS_MISMATCH = "CURRENTNESS_MISMATCH"
    REPLAY_DETECTED = "REPLAY_DETECTED"
    RESOURCE_SCOPE_WIDENING = "RESOURCE_SCOPE_WIDENING"
    ACTION_SCOPE_WIDENING = "ACTION_SCOPE_WIDENING"
    CAPABILITY_WIDENING = "CAPABILITY_WIDENING"
    INVALID_EFFECT_ID = "INVALID_EFFECT_ID"
    INVALID_RUNTIME_IDENTITY = "INVALID_RUNTIME_IDENTITY"
    INVALID_DIGEST = "INVALID_DIGEST"
    INVALID_REQUEST = "INVALID_REQUEST"


@dataclass(frozen=True)
class RequestedRuntimeEffect:
    effect_id: str
    action_digest: str
    effect_type: str
    resource_scope: Tuple[str, ...]
    action_scope: Tuple[str, ...]
    correlation_id: str
    requested_capabilities: Tuple[str, ...]


@dataclass(frozen=True)
class RuntimeIdentityBinding:
    runtime_id: str
    runtime_role: RuntimeRole
    execution_domain: str
    workload_identity: str
    artifact_digest: str
    currentness_token: str


@dataclass(frozen=True)
class PDPResultBinding:
    pdp_result_id: str
    decision: PDPDecision
    proposal_digest: str
    action_digest: str
    authorized_resource_scope: Tuple[str, ...]
    authorized_action_scope: Tuple[str, ...]
    authorized_capabilities: Tuple[str, ...]
    expected_runtime_identity_digest: str
    authority_currentness_token: str
    request_nonce: str


@dataclass(frozen=True)
class RuntimeAdmissionRequest:
    pdp_result: PDPResultBinding
    requested_effect: RequestedRuntimeEffect
    runtime_identity: RuntimeIdentityBinding
    presented_currentness_token: str
    request_nonce: str


@dataclass(frozen=True)
class AdmissionValidationContext:
    seen_nonces: FrozenSet[str]


@dataclass(frozen=True)
class RuntimeAdmissionDecision:
    decision: AdmissionDecision
    reason: AdmissionReason
    request_digest: str
    runtime_identity_digest: str
    effect_digest: str


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_runtime_identity(binding: RuntimeIdentityBinding) -> str:
    payload = {
        "artifact_digest": binding.artifact_digest,
        "currentness_token": binding.currentness_token,
        "execution_domain": binding.execution_domain,
        "runtime_id": binding.runtime_id,
        "runtime_role": binding.runtime_role.value,
        "workload_identity": binding.workload_identity,
    }
    return _canonical_json(payload)


def runtime_identity_digest(binding: RuntimeIdentityBinding) -> str:
    return _sha256_text(canonical_runtime_identity(binding))


def canonical_requested_effect(effect: RequestedRuntimeEffect) -> str:
    payload = {
        "action_digest": effect.action_digest,
        "action_scope": sorted(effect.action_scope),
        "correlation_id": effect.correlation_id,
        "effect_id": effect.effect_id,
        "effect_type": effect.effect_type,
        "requested_capabilities": sorted(effect.requested_capabilities),
        "resource_scope": sorted(effect.resource_scope),
    }
    return _canonical_json(payload)


def requested_effect_digest(effect: RequestedRuntimeEffect) -> str:
    return _sha256_text(canonical_requested_effect(effect))


def canonical_admission_request(request: RuntimeAdmissionRequest) -> str:
    pdp = request.pdp_result
    payload = {
        "pdp_result": {
            "action_digest": pdp.action_digest,
            "authority_currentness_token": pdp.authority_currentness_token,
            "authorized_action_scope": sorted(pdp.authorized_action_scope),
            "authorized_capabilities": sorted(pdp.authorized_capabilities),
            "authorized_resource_scope": sorted(pdp.authorized_resource_scope),
            "decision": pdp.decision.value,
            "expected_runtime_identity_digest": pdp.expected_runtime_identity_digest,
            "pdp_result_id": pdp.pdp_result_id,
            "proposal_digest": pdp.proposal_digest,
            "request_nonce": pdp.request_nonce,
        },
        "presented_currentness_token": request.presented_currentness_token,
        "request_nonce": request.request_nonce,
        "requested_effect": json.loads(canonical_requested_effect(request.requested_effect)),
        "runtime_identity": json.loads(canonical_runtime_identity(request.runtime_identity)),
    }
    return _canonical_json(payload)


def admission_request_digest(request: RuntimeAdmissionRequest) -> str:
    return _sha256_text(canonical_admission_request(request))
