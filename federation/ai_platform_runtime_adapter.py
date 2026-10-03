"""Explicit ai_platform -> SWARM runtime-contract adapter.

This module maps an exact, already-governed ai_platform runtime identity/effect
projection into SWARM's deterministic admission data model. It does not create
a PDP ALLOW, capability grant, executor, credential or external effect.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json,re
from typing import Mapping,Any

from runtime.contracts import (
    PDPDecision,PDPResultBinding,RequestedRuntimeEffect,RuntimeIdentityBinding,
    RuntimeAdmissionRequest,RuntimeRole,runtime_identity_digest,
)

SHA=re.compile(r"^[0-9a-f]{64}$")
class FederationRuntimeAdapterError(ValueError): pass

def _txt(v,n):
    if not isinstance(v,str) or not v.strip() or "\x00" in v: raise FederationRuntimeAdapterError(n)
    return v
def _sha(v,n):
    _txt(v,n)
    if SHA.fullmatch(v) is None: raise FederationRuntimeAdapterError(n)
    return v
def _tuple(v,n):
    if not isinstance(v,(list,tuple)) or not v or any(not isinstance(x,str) or not x.strip() for x in v): raise FederationRuntimeAdapterError(n)
    t=tuple(v)
    if len(t)!=len(set(t)): raise FederationRuntimeAdapterError(n)
    return t

@dataclass(frozen=True)
class AiPlatformRuntimeProjection:
    proposal_id:str
    mission_id:str
    workload_identity:str
    execution_subject:str
    runtime_instance_id:str
    sandbox_id:str
    workspace_id:str
    runtime_attestation_digest:str
    provisioned_executor_digest:str
    requested_effect_id:str
    policy_binding:str
    authority_lineage_digest:str
    requested_authority:str
    action_class:str
    resource:str
    payload_digest:str
    observability_state:str
    ai_platform_runtime_identity_digest:str
    ai_platform_requested_effect_digest:str

    @classmethod
    def from_mapping(cls,value:Mapping[str,Any])->"AiPlatformRuntimeProjection":
        if not isinstance(value,Mapping) or set(value)!={f.name for f in cls.__dataclass_fields__.values()}:
            raise FederationRuntimeAdapterError("projection fields")
        obj=cls(**dict(value))
        for n in ("proposal_id","mission_id","workload_identity","execution_subject","runtime_instance_id","sandbox_id","workspace_id","requested_effect_id","policy_binding","requested_authority","action_class","resource","observability_state"):
            _txt(getattr(obj,n),n)
        for n in ("runtime_attestation_digest","provisioned_executor_digest","authority_lineage_digest","payload_digest","ai_platform_runtime_identity_digest","ai_platform_requested_effect_digest"):
            _sha(getattr(obj,n),n)
        return obj

@dataclass(frozen=True)
class SwarmAdapterPolicy:
    runtime_role:RuntimeRole
    execution_domain:str
    artifact_digest:str
    currentness_token:str
    effect_type:str
    resource_scope:tuple[str,...]
    action_scope:tuple[str,...]
    correlation_id:str
    requested_capabilities:tuple[str,...]
    action_digest:str
    pdp_result_id:str
    proposal_digest:str
    authorized_resource_scope:tuple[str,...]
    authorized_action_scope:tuple[str,...]
    authorized_capabilities:tuple[str,...]
    request_nonce:str

    def validate(self):
        if not isinstance(self.runtime_role,RuntimeRole): raise FederationRuntimeAdapterError("runtime_role")
        for n in ("execution_domain","currentness_token","effect_type","correlation_id","pdp_result_id","request_nonce"):
            _txt(getattr(self,n),n)
        for n in ("artifact_digest","action_digest","proposal_digest"):
            _sha(getattr(self,n),n)
        for n in ("resource_scope","action_scope","requested_capabilities","authorized_resource_scope","authorized_action_scope","authorized_capabilities"):
            _tuple(getattr(self,n),n)
        return self

def _projection_digest(p:AiPlatformRuntimeProjection)->str:
    raw=json.dumps(p.__dict__,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return sha256(b"LION/SWARM-AI-PLATFORM-PROJECTION/1\0"+raw).hexdigest()

def adapt_to_swarm_request(
    projection:AiPlatformRuntimeProjection,
    policy:SwarmAdapterPolicy,
)->RuntimeAdmissionRequest:
    projection=projection if isinstance(projection,AiPlatformRuntimeProjection) else AiPlatformRuntimeProjection.from_mapping(projection)
    projection.from_mapping(projection.__dict__)
    policy.validate()
    identity=RuntimeIdentityBinding(
        runtime_id=projection.runtime_instance_id,
        runtime_role=policy.runtime_role,
        execution_domain=policy.execution_domain,
        workload_identity=projection.workload_identity,
        artifact_digest=policy.artifact_digest,
        currentness_token=policy.currentness_token,
    )
    effect=RequestedRuntimeEffect(
        effect_id=projection.requested_effect_id,
        action_digest=policy.action_digest,
        effect_type=policy.effect_type,
        resource_scope=policy.resource_scope,
        action_scope=policy.action_scope,
        correlation_id=policy.correlation_id,
        requested_capabilities=policy.requested_capabilities,
    )
    pdp=PDPResultBinding(
        pdp_result_id=policy.pdp_result_id,
        decision=PDPDecision.ALLOW,
        proposal_digest=policy.proposal_digest,
        action_digest=policy.action_digest,
        authorized_resource_scope=policy.authorized_resource_scope,
        authorized_action_scope=policy.authorized_action_scope,
        authorized_capabilities=policy.authorized_capabilities,
        expected_runtime_identity_digest=runtime_identity_digest(identity),
        authority_currentness_token=policy.currentness_token,
        request_nonce=policy.request_nonce,
    )
    return RuntimeAdmissionRequest(
        pdp_result=pdp,requested_effect=effect,runtime_identity=identity,
        presented_currentness_token=policy.currentness_token,request_nonce=policy.request_nonce,
    )

def adapter_evidence(projection:AiPlatformRuntimeProjection,request:RuntimeAdmissionRequest)->dict[str,str]:
    return {
        "projection_digest":_projection_digest(projection),
        "ai_platform_runtime_identity_digest":projection.ai_platform_runtime_identity_digest,
        "ai_platform_requested_effect_digest":projection.ai_platform_requested_effect_digest,
        "swarm_runtime_identity_digest":runtime_identity_digest(request.runtime_identity),
        "authority_effect":"NONE","execution_effect":"NONE",
    }
