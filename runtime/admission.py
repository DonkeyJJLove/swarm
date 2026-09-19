"""Deterministic fail-closed runtime admission evaluation.

This module does not execute effects. ADMIT is a binding decision, not an effect.
"""

from __future__ import annotations

from .contracts import (
    AdmissionDecision,
    AdmissionReason,
    AdmissionValidationContext,
    PDPDecision,
    PDPResultBinding,
    RuntimeAdmissionDecision,
    RuntimeAdmissionRequest,
    RuntimeIdentityBinding,
    RuntimeRole,
    RequestedRuntimeEffect,
    admission_request_digest,
    requested_effect_digest,
    runtime_identity_digest,
)


_HEX = frozenset("0123456789abcdefABCDEF")


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in _HEX for ch in value)


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid_items(values: object) -> bool:
    return (
        isinstance(values, tuple)
        and all(isinstance(item, str) and bool(item.strip()) for item in values)
    )


def _identity_is_valid(binding: RuntimeIdentityBinding) -> bool:
    return (
        _nonempty(binding.runtime_id)
        and isinstance(binding.runtime_role, RuntimeRole)
        and _nonempty(binding.execution_domain)
        and _nonempty(binding.workload_identity)
        and _is_sha256(binding.artifact_digest)
        and _nonempty(binding.currentness_token)
    )


def _effect_is_structurally_valid(effect: RequestedRuntimeEffect) -> bool:
    return (
        _nonempty(effect.effect_type)
        and _nonempty(effect.correlation_id)
        and _valid_items(effect.resource_scope)
        and _valid_items(effect.action_scope)
        and _valid_items(effect.requested_capabilities)
    )


def _deny(
    request: RuntimeAdmissionRequest,
    reason: AdmissionReason,
) -> RuntimeAdmissionDecision:
    try:
        identity_digest = runtime_identity_digest(request.runtime_identity)
    except Exception:
        identity_digest = ""
    try:
        effect_digest = requested_effect_digest(request.requested_effect)
    except Exception:
        effect_digest = ""
    try:
        request_digest = admission_request_digest(request)
    except Exception:
        request_digest = ""
    return RuntimeAdmissionDecision(
        decision=AdmissionDecision.DENY,
        reason=reason,
        request_digest=request_digest,
        runtime_identity_digest=identity_digest,
        effect_digest=effect_digest,
    )


def evaluate_runtime_admission(
    request: RuntimeAdmissionRequest,
    context: AdmissionValidationContext,
) -> RuntimeAdmissionDecision:
    if not isinstance(request, RuntimeAdmissionRequest) or not isinstance(
        context, AdmissionValidationContext
    ):
        return _deny(request, AdmissionReason.INVALID_REQUEST)

    effect = request.requested_effect
    identity = request.runtime_identity
    pdp = request.pdp_result

    if not isinstance(effect, RequestedRuntimeEffect):
        return _deny(request, AdmissionReason.INVALID_REQUEST)
    if not isinstance(identity, RuntimeIdentityBinding):
        return _deny(request, AdmissionReason.INVALID_REQUEST)
    if not isinstance(pdp, PDPResultBinding):
        return _deny(request, AdmissionReason.INVALID_REQUEST)
    if not isinstance(pdp.decision, PDPDecision):
        return _deny(request, AdmissionReason.INVALID_REQUEST)
    if not isinstance(context.seen_nonces, frozenset) or not all(
        _nonempty(value) for value in context.seen_nonces
    ):
        return _deny(request, AdmissionReason.INVALID_REQUEST)

    if not _nonempty(effect.effect_id):
        return _deny(request, AdmissionReason.INVALID_EFFECT_ID)
    if not _identity_is_valid(identity):
        if not _is_sha256(identity.artifact_digest):
            return _deny(request, AdmissionReason.INVALID_DIGEST)
        return _deny(request, AdmissionReason.INVALID_RUNTIME_IDENTITY)
    if not _effect_is_structurally_valid(effect):
        return _deny(request, AdmissionReason.INVALID_REQUEST)

    digest_fields = (
        effect.action_digest,
        identity.artifact_digest,
        pdp.proposal_digest,
        pdp.action_digest,
        pdp.expected_runtime_identity_digest,
    )
    if not all(_is_sha256(value) for value in digest_fields):
        return _deny(request, AdmissionReason.INVALID_DIGEST)

    if not all(
        _nonempty(value)
        for value in (
            pdp.pdp_result_id,
            pdp.authority_currentness_token,
            pdp.request_nonce,
            request.presented_currentness_token,
            request.request_nonce,
        )
    ):
        return _deny(request, AdmissionReason.INVALID_REQUEST)

    if not all(
        _valid_items(values)
        for values in (
            pdp.authorized_resource_scope,
            pdp.authorized_action_scope,
            pdp.authorized_capabilities,
        )
    ):
        return _deny(request, AdmissionReason.INVALID_REQUEST)

    if pdp.decision != PDPDecision.ALLOW:
        return _deny(request, AdmissionReason.PDP_NOT_ALLOW)

    if effect.action_digest != pdp.action_digest:
        return _deny(request, AdmissionReason.ACTION_DIGEST_MISMATCH)

    identity_digest = runtime_identity_digest(identity)
    if identity_digest != pdp.expected_runtime_identity_digest:
        return _deny(request, AdmissionReason.RUNTIME_IDENTITY_MISMATCH)

    if (
        request.presented_currentness_token != pdp.authority_currentness_token
        or identity.currentness_token != pdp.authority_currentness_token
    ):
        return _deny(request, AdmissionReason.CURRENTNESS_MISMATCH)

    if request.request_nonce != pdp.request_nonce:
        return _deny(request, AdmissionReason.INVALID_REQUEST)

    if request.request_nonce in context.seen_nonces:
        return _deny(request, AdmissionReason.REPLAY_DETECTED)

    if not set(effect.resource_scope).issubset(set(pdp.authorized_resource_scope)):
        return _deny(request, AdmissionReason.RESOURCE_SCOPE_WIDENING)

    if not set(effect.action_scope).issubset(set(pdp.authorized_action_scope)):
        return _deny(request, AdmissionReason.ACTION_SCOPE_WIDENING)

    if not set(effect.requested_capabilities).issubset(
        set(pdp.authorized_capabilities)
    ):
        return _deny(request, AdmissionReason.CAPABILITY_WIDENING)

    return RuntimeAdmissionDecision(
        decision=AdmissionDecision.ADMIT,
        reason=AdmissionReason.ADMITTED,
        request_digest=admission_request_digest(request),
        runtime_identity_digest=identity_digest,
        effect_digest=requested_effect_digest(effect),
    )
