from __future__ import annotations

from dataclasses import fields, replace
import ast
import hashlib
from pathlib import Path
import unittest

from runtime import (
    AdmissionDecision,
    AdmissionReason,
    AdmissionValidationContext,
    PDPDecision,
    PDPResultBinding,
    RequestedRuntimeEffect,
    RuntimeAdmissionRequest,
    RuntimeIdentityBinding,
    RuntimeRole,
    admission_request_digest,
    canonical_runtime_identity,
    evaluate_runtime_admission,
    runtime_identity_digest,
)


ROOT = Path(__file__).resolve().parents[1]
SHA_ACTION = hashlib.sha256(b"action").hexdigest()
SHA_PROPOSAL = hashlib.sha256(b"proposal").hexdigest()
SHA_ARTIFACT = hashlib.sha256(b"artifact").hexdigest()


def make_identity(**changes):
    value = RuntimeIdentityBinding(
        runtime_id="runtime-1",
        runtime_role=RuntimeRole.AGENT_WORKLOAD,
        execution_domain="lab.example",
        workload_identity="agent/example-1",
        artifact_digest=SHA_ARTIFACT,
        currentness_token="authority-v1",
    )
    return replace(value, **changes)


def make_effect(**changes):
    value = RequestedRuntimeEffect(
        effect_id="effect-1",
        action_digest=SHA_ACTION,
        effect_type="read.telemetry",
        resource_scope=("telemetry/drone-1",),
        action_scope=("read",),
        correlation_id="corr-1",
        requested_capabilities=("telemetry.read",),
    )
    return replace(value, **changes)


def make_request(
    *,
    decision=PDPDecision.ALLOW,
    identity=None,
    effect=None,
    seen_identity_digest=None,
    **request_changes,
):
    identity = identity or make_identity()
    effect = effect or make_effect()
    pdp = PDPResultBinding(
        pdp_result_id="pdp-1",
        decision=decision,
        proposal_digest=SHA_PROPOSAL,
        action_digest=SHA_ACTION,
        authorized_resource_scope=("telemetry/drone-1",),
        authorized_action_scope=("read",),
        authorized_capabilities=("telemetry.read",),
        expected_runtime_identity_digest=(
            seen_identity_digest or runtime_identity_digest(identity)
        ),
        authority_currentness_token="authority-v1",
        request_nonce="nonce-1",
    )
    request = RuntimeAdmissionRequest(
        pdp_result=pdp,
        requested_effect=effect,
        runtime_identity=identity,
        presented_currentness_token="authority-v1",
        request_nonce="nonce-1",
    )
    return replace(request, **request_changes)


def decide(request, seen=()):
    return evaluate_runtime_admission(
        request,
        AdmissionValidationContext(seen_nonces=frozenset(seen)),
    )


class RuntimeAdmissionContractTests(unittest.TestCase):
    def assertDenied(self, decision, reason):
        self.assertEqual(decision.decision, AdmissionDecision.DENY)
        self.assertEqual(decision.reason, reason)

    def test_01_exact_valid_binding_admits(self):
        result = decide(make_request())
        self.assertEqual(result.decision, AdmissionDecision.ADMIT)
        self.assertEqual(result.reason, AdmissionReason.ADMITTED)

    def test_02_pdp_deny_denies(self):
        self.assertDenied(
            decide(make_request(decision=PDPDecision.DENY)),
            AdmissionReason.PDP_NOT_ALLOW,
        )

    def test_03_action_digest_mismatch_denies(self):
        effect = make_effect(action_digest=hashlib.sha256(b"other").hexdigest())
        self.assertDenied(
            decide(make_request(effect=effect)),
            AdmissionReason.ACTION_DIGEST_MISMATCH,
        )

    def test_04_runtime_identity_mismatch_denies(self):
        identity = make_identity(runtime_id="runtime-other")
        self.assertDenied(
            decide(make_request(identity=identity, seen_identity_digest=hashlib.sha256(b"expected").hexdigest())),
            AdmissionReason.RUNTIME_IDENTITY_MISMATCH,
        )

    def test_05_currentness_mismatch_denies(self):
        req = make_request()
        req = replace(req, presented_currentness_token="authority-old")
        self.assertDenied(decide(req), AdmissionReason.CURRENTNESS_MISMATCH)

    def test_06_replayed_nonce_denies(self):
        self.assertDenied(
            decide(make_request(), seen={"nonce-1"}),
            AdmissionReason.REPLAY_DETECTED,
        )

    def test_07_resource_scope_widening_denies(self):
        effect = make_effect(resource_scope=("telemetry/drone-1", "telemetry/drone-2"))
        self.assertDenied(
            decide(make_request(effect=effect)),
            AdmissionReason.RESOURCE_SCOPE_WIDENING,
        )

    def test_08_action_scope_widening_denies(self):
        effect = make_effect(action_scope=("read", "write"))
        self.assertDenied(
            decide(make_request(effect=effect)),
            AdmissionReason.ACTION_SCOPE_WIDENING,
        )

    def test_09_capability_widening_denies(self):
        effect = make_effect(requested_capabilities=("telemetry.read", "telemetry.write"))
        self.assertDenied(
            decide(make_request(effect=effect)),
            AdmissionReason.CAPABILITY_WIDENING,
        )

    def test_10_empty_runtime_id_denies(self):
        identity = make_identity(runtime_id="")
        self.assertDenied(
            decide(make_request(identity=identity)),
            AdmissionReason.INVALID_RUNTIME_IDENTITY,
        )

    def test_11_invalid_action_digest_denies(self):
        effect = make_effect(action_digest="not-a-digest")
        self.assertDenied(
            decide(make_request(effect=effect)),
            AdmissionReason.INVALID_DIGEST,
        )

    def test_12_invalid_artifact_digest_denies(self):
        identity = make_identity(artifact_digest="not-a-digest")
        self.assertDenied(
            decide(make_request(identity=identity)),
            AdmissionReason.INVALID_DIGEST,
        )

    def test_13_wildcard_resource_not_authorized_denies(self):
        effect = make_effect(resource_scope=("*",))
        self.assertDenied(
            decide(make_request(effect=effect)),
            AdmissionReason.RESOURCE_SCOPE_WIDENING,
        )

    def test_14_wildcard_action_not_authorized_denies(self):
        effect = make_effect(action_scope=("*",))
        self.assertDenied(
            decide(make_request(effect=effect)),
            AdmissionReason.ACTION_SCOPE_WIDENING,
        )

    def test_15_model_provider_metadata_cannot_alter_decision(self):
        request_fields = {field.name for field in fields(RuntimeAdmissionRequest)}
        identity_fields = {field.name for field in fields(RuntimeIdentityBinding)}
        self.assertTrue({"model", "provider", "model_provider"}.isdisjoint(request_fields))
        self.assertTrue({"model", "provider", "model_provider"}.isdisjoint(identity_fields))
        metadata_a = {"provider": "alpha", "model": "m1"}
        metadata_b = {"provider": "beta", "model": "m2"}
        self.assertNotEqual(metadata_a, metadata_b)
        self.assertEqual(decide(make_request()), decide(make_request()))

    def test_16_canonical_identity_serialization_is_deterministic(self):
        identity = make_identity()
        self.assertEqual(
            canonical_runtime_identity(identity),
            canonical_runtime_identity(identity),
        )
        self.assertEqual(
            runtime_identity_digest(identity),
            runtime_identity_digest(identity),
        )

    def test_17_admission_request_digest_is_deterministic(self):
        request = make_request()
        self.assertEqual(
            admission_request_digest(request),
            admission_request_digest(request),
        )

    def test_18_runtime_package_has_no_execution_surface(self):
        forbidden_imports = {
            "subprocess", "socket", "requests", "urllib", "kubernetes",
            "docker", "paramiko", "shlex", "pty",
        }
        forbidden_calls = {"system", "popen", "exec", "eval"}
        forbidden_names = {"execute", "launch", "spawn", "run_effect", "apply_effect"}
        for path in sorted((ROOT / "runtime").glob("*.py")):
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("shell=True", source, path.as_posix())
            self.assertNotIn("os.system", source, path.as_posix())
            tree = ast.parse(source, filename=path.as_posix())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn(alias.name.split(".")[0], forbidden_imports)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.assertNotIn(node.module.split(".")[0], forbidden_imports)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self.assertNotIn(node.name, forbidden_names)
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        self.assertNotIn(node.func.attr, forbidden_calls)


if __name__ == "__main__":
    unittest.main(verbosity=2)
