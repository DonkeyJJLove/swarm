"""SWARM generic runtime contracts.

Contract-only Phase 2 entry. No executor or effect provider is exposed here.
"""

from .admission import evaluate_runtime_admission
from .contracts import (
    AdmissionDecision,
    AdmissionReason,
    AdmissionValidationContext,
    PDPDecision,
    PDPResultBinding,
    RequestedRuntimeEffect,
    RuntimeAdmissionDecision,
    RuntimeAdmissionRequest,
    RuntimeIdentityBinding,
    RuntimeRole,
    admission_request_digest,
    canonical_admission_request,
    canonical_runtime_identity,
    requested_effect_digest,
    runtime_identity_digest,
)

__all__ = [
    "AdmissionDecision",
    "AdmissionReason",
    "AdmissionValidationContext",
    "PDPDecision",
    "PDPResultBinding",
    "RequestedRuntimeEffect",
    "RuntimeAdmissionDecision",
    "RuntimeAdmissionRequest",
    "RuntimeIdentityBinding",
    "RuntimeRole",
    "admission_request_digest",
    "canonical_admission_request",
    "canonical_runtime_identity",
    "evaluate_runtime_admission",
    "requested_effect_digest",
    "runtime_identity_digest",
]
