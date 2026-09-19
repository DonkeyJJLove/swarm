from __future__ import annotations

from dataclasses import replace
import ast
from pathlib import Path
import unittest

from runtime.examples.drone_identity_prerequisites import (
    DRONE_IDENTITY_PREREQUISITE_QUALIFICATION as DRONE_QUALIFICATION,
)
from runtime.identity_prerequisites import (
    CANONICAL_IDENTITY_SOURCES,
    IdentityPrerequisiteEvidence,
    IdentityPrerequisiteStatus,
    MissingIdentityRequirement,
    SWARM_RUNTIME_IDENTITY_SCHEMA_EQ_F009,
    canonical_evidence_digest,
    canonical_source_reference_digest,
    qualify_identity_prerequisites,
)


ROOT = Path(__file__).resolve().parents[1]
SHA = "a" * 64


def complete_evidence(**changes):
    value = IdentityPrerequisiteEvidence(
        agent_registry_instance_id="instance-1",
        agent_registry_agent_id="agent-1",
        agent_registry_spec_version="1",
        agent_registry_spec_digest=SHA,
        agent_registry_state="ACTIVE",
        agent_registry_generation=0,
        agent_registry_evidence_refs=("registry:event:1",),
        workload_identity="workload:drone-example",
        immutable_image_digest=SHA,
        runtime_instance_id="runtime-1",
        sandbox_id="sandbox-1",
        workspace_id="workspace-1",
        runtime_attestation_digest=SHA,
        provisioned_executor_digest=SHA,
        authority_currentness_evidence="currentness:evidence:1",
        source_refs=CANONICAL_IDENTITY_SOURCES,
        schema_compatibility_qualified=True,
    )
    return replace(value, **changes)


class IdentityPrerequisiteTests(unittest.TestCase):
    def assertNotReadyWith(self, evidence, reason):
        result = qualify_identity_prerequisites(evidence)
        self.assertEqual(result.status, IdentityPrerequisiteStatus.NOT_READY)
        self.assertIn(reason, result.missing_requirements)

    def test_01_current_drone_qualification_is_not_ready(self):
        self.assertEqual(DRONE_QUALIFICATION.status, IdentityPrerequisiteStatus.NOT_READY)

    def test_02_missing_agent_instance_denies_ready(self):
        self.assertNotReadyWith(
            complete_evidence(agent_registry_instance_id=None),
            MissingIdentityRequirement.AGENT_INSTANCE_MISSING,
        )

    def test_03_inactive_agent_instance_denies_ready(self):
        self.assertNotReadyWith(
            complete_evidence(agent_registry_state="REGISTERED"),
            MissingIdentityRequirement.AGENT_INSTANCE_NOT_ACTIVE,
        )

    def test_04_empty_agent_registry_evidence_refs_deny_ready(self):
        self.assertNotReadyWith(
            complete_evidence(agent_registry_evidence_refs=()),
            MissingIdentityRequirement.AGENT_EVIDENCE_MISSING,
        )

    def test_05_mutable_image_tag_cannot_satisfy_image_digest(self):
        self.assertNotReadyWith(
            complete_evidence(immutable_image_digest="localhost:5000/drone:latest"),
            MissingIdentityRequirement.IMMUTABLE_ARTIFACT_MISSING,
        )

    def test_06_malformed_image_digest_denies_ready(self):
        self.assertNotReadyWith(
            complete_evidence(immutable_image_digest="not-a-sha256"),
            MissingIdentityRequirement.IMMUTABLE_ARTIFACT_MISSING,
        )

    def test_07_missing_runtime_instance_id_denies_ready(self):
        self.assertNotReadyWith(
            complete_evidence(runtime_instance_id=None),
            MissingIdentityRequirement.RUNTIME_INSTANCE_MISSING,
        )

    def test_08_missing_runtime_attestation_denies_ready(self):
        self.assertNotReadyWith(
            complete_evidence(runtime_attestation_digest=None),
            MissingIdentityRequirement.RUNTIME_ATTESTATION_MISSING,
        )

    def test_09_missing_provisioned_executor_denies_ready(self):
        self.assertNotReadyWith(
            complete_evidence(provisioned_executor_digest=None),
            MissingIdentityRequirement.PROVISIONED_EXECUTOR_MISSING,
        )

    def test_10_missing_currentness_evidence_denies_ready(self):
        self.assertNotReadyWith(
            complete_evidence(authority_currentness_evidence=None),
            MissingIdentityRequirement.CURRENTNESS_EVIDENCE_MISSING,
        )

    def test_11_unresolved_schema_compatibility_denies_ready(self):
        self.assertFalse(SWARM_RUNTIME_IDENTITY_SCHEMA_EQ_F009)
        self.assertNotReadyWith(
            complete_evidence(schema_compatibility_qualified=False),
            MissingIdentityRequirement.SCHEMA_COMPATIBILITY_UNRESOLVED,
        )

    def test_12_complete_synthetic_prerequisites_can_be_ready(self):
        result = qualify_identity_prerequisites(complete_evidence())
        self.assertEqual(result.status, IdentityPrerequisiteStatus.READY)
        self.assertEqual(result.missing_requirements, ())

    def test_13_ready_still_does_not_create_runtime_identity_binding(self):
        result = qualify_identity_prerequisites(complete_evidence())
        self.assertEqual(result.status, IdentityPrerequisiteStatus.READY)
        self.assertFalse(hasattr(result, "runtime_identity"))
        tree = ast.parse((ROOT / "runtime/identity_prerequisites.py").read_text(encoding="utf-8"))
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertNotIn("RuntimeIdentityBinding", calls)

    def test_14_no_agent_instance_is_created(self):
        tree = ast.parse((ROOT / "runtime/identity_prerequisites.py").read_text(encoding="utf-8"))
        calls = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertNotIn("AgentInstance", calls)

    def test_15_no_authority_contract_is_created(self):
        forbidden = {
            "RequestedRuntimeEffect", "PDPResultBinding", "RuntimeAdmissionRequest",
            "CapabilityLease", "AgentSpec",
        }
        for path in (
            ROOT / "runtime/identity_prerequisites.py",
            ROOT / "runtime/examples/drone_identity_prerequisites.py",
        ):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            calls = {
                node.func.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            self.assertTrue(forbidden.isdisjoint(calls))

    def test_16_source_reference_digest_is_deterministic(self):
        self.assertEqual(
            canonical_source_reference_digest(),
            canonical_source_reference_digest(),
        )

    def test_17_evidence_digest_is_deterministic(self):
        evidence = complete_evidence()
        self.assertEqual(
            canonical_evidence_digest(evidence),
            canonical_evidence_digest(evidence),
        )

    def test_18_modules_have_no_effect_capable_imports_or_calls(self):
        forbidden_imports = {
            "subprocess", "socket", "requests", "urllib", "kubernetes",
            "docker", "paramiko", "shlex", "pty", "os",
        }
        forbidden_calls = {
            "open", "connect", "send", "sendto", "bind", "listen",
            "system", "popen", "run", "call", "spawn",
        }
        for path in (
            ROOT / "runtime/identity_prerequisites.py",
            ROOT / "runtime/examples/drone_identity_prerequisites.py",
        ):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertNotIn(alias.name.split(".")[0], forbidden_imports)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    self.assertNotIn(node.module.split(".")[0], forbidden_imports)
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.assertNotIn(node.func.id, forbidden_calls)
                    elif isinstance(node.func, ast.Attribute):
                        self.assertNotIn(node.func.attr, forbidden_calls)


if __name__ == "__main__":
    unittest.main(verbosity=2)
