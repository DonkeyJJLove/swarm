from __future__ import annotations

from dataclasses import FrozenInstanceError, asdict
import ast
import hashlib
import json
from pathlib import Path
import re
import unittest

from runtime.contracts import RuntimeRole
from runtime.examples.drone_agent_workload import DRONE_AGENT_WORKLOAD_EXAMPLE as E


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "drones/drone_logic.py": "96c3544d07804c770284521fbac2030d71a72d3d",
    "drones/drone-deployment.yaml": "1d291aa0d29d2e40a180997dbcb5d4616e9ccaca",
    "drones/drone-service.yaml": "338a0a0e2bca0f56b69b7cd4f8aaabfb1016349f",
    "drones/Dockerfile": "a022830350bdbfe03e2070d633da28a27b6cec23",
    "security/policies/network-policy.yaml": "4a99a5a1409495b4a8e6ea156af4211a38222d47",
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def git_blob_sha(path: str) -> str:
    data = (ROOT / path).read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class AgentWorkloadExampleTests(unittest.TestCase):
    def test_01_role_is_agent_workload(self):
        self.assertEqual(E.runtime_role, RuntimeRole.AGENT_WORKLOAD)

    def test_02_source_master_is_qualified_merge(self):
        self.assertEqual(E.source_master_sha, "7301c815127b52b8f40858a54f3fe8e905798312")

    def test_03_all_source_evidence_paths_and_blobs_are_exact(self):
        self.assertEqual({item.path: item.blob_sha for item in E.source_evidence}, EXPECTED)
        for path, expected in EXPECTED.items():
            with self.subTest(path=path):
                self.assertEqual(git_blob_sha(path), expected)

    def test_04_deployment_identity_and_replica_count_match_source(self):
        deployment = read("drones/drone-deployment.yaml")
        for value in ("kind: Deployment", "name: drone", "namespace: laboratory-swarm", "replicas: 10"):
            self.assertIn(value, deployment)
        self.assertEqual((E.workload_kind, E.namespace, E.workload_name, E.declared_replicas),
                         ("Deployment", "laboratory-swarm", "drone", 10))

    def test_05_container_and_image_match_source(self):
        deployment = read("drones/drone-deployment.yaml")
        self.assertIn("- name: drone", deployment)
        self.assertIn("image: localhost:5000/drone:latest", deployment)
        self.assertEqual((E.container_name, E.image_reference),
                         ("drone", "localhost:5000/drone:latest"))

    def test_06_mutable_image_keeps_artifact_identity_unresolved(self):
        self.assertTrue(E.image_reference.endswith(":latest"))
        self.assertNotIn("@sha256:", E.image_reference)
        self.assertEqual(E.artifact_identity_status, "UNRESOLVED_MUTABLE_TAG")

    def test_07_drone_id_derives_from_metadata_name(self):
        self.assertRegex(read("drones/drone-deployment.yaml"),
                         r"name:\s*DRONE_ID[\s\S]*?fieldPath:\s*metadata\.name")
        self.assertEqual(E.runtime_identifier_source, "metadata.name")

    def test_08_drone_id_is_not_agent_instance_id(self):
        example_source = read("runtime/examples/drone_agent_workload.py")
        self.assertEqual(E.runtime_identifier_classification, "INFRASTRUCTURE_RUNTIME_IDENTIFIER")
        self.assertEqual(E.agent_identity_status, "UNBOUND")
        self.assertNotIn("agent_instance_id", example_source)

    def test_09_drone_deployment_has_no_service_account_binding(self):
        self.assertNotIn("serviceAccountName", read("drones/drone-deployment.yaml"))
        self.assertEqual(E.service_account_binding_status, "ABSENT")

    def test_10_application_observes_udp_to_aggregator_6000(self):
        source = read("drones/drone_logic.py")
        for value in ("aggregator-service.laboratory-swarm.svc.cluster.local",
                      '"6000"', "socket.SOCK_DGRAM", "sock.sendto("):
            self.assertIn(value, source)
        self.assertEqual(E.observed_application_channels,
                         ("UDP -> aggregator-service.laboratory-swarm.svc.cluster.local:6000",))

    def test_11_mqtt_configuration_is_declared_but_not_used_by_application(self):
        deployment = read("drones/drone-deployment.yaml")
        source = read("drones/drone_logic.py")
        self.assertIn("MQTT_BROKER", deployment)
        self.assertIn("MQTT_PORT", deployment)
        self.assertNotIn("MQTT_BROKER", source)
        self.assertNotIn("MQTT_PORT", source)

    def test_12_tcp_7000_is_declared_without_application_listener(self):
        deployment = read("drones/drone-deployment.yaml")
        service = read("drones/drone-service.yaml")
        source = read("drones/drone_logic.py")
        self.assertIn("containerPort: 7000", deployment)
        self.assertIn("targetPort: 7000", service)
        self.assertIn("TCP/7000", E.manifest_declared_ports)
        self.assertNotIn("7000", source)
        self.assertNotRegex(source, r"\.(bind|listen)\s*\(")

    def test_13_current_network_policy_does_not_select_drone_pods(self):
        policy = read("security/policies/network-policy.yaml")
        match = re.search(r"podSelector:\s*\n\s*matchLabels:\s*\n\s*app:\s*([^\s]+)", policy)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "aggregator")
        self.assertEqual(E.network_policy_binding_status, "NO_DRONE_SELECTOR_OBSERVED")

    def test_14_runtime_identity_is_not_materialized(self):
        self.assertEqual(E.runtime_identity_status, "NOT_MATERIALIZED")

    def test_15_authority_status_is_none(self):
        self.assertEqual(E.authority_status, "NONE")

    def test_16_example_package_does_not_construct_authority_contracts(self):
        forbidden = {
            "RuntimeIdentityBinding", "PDPResultBinding", "RuntimeAdmissionRequest",
            "RequestedRuntimeEffect", "CapabilityLease", "AgentSpec", "SwarmSpec",
        }
        for path in sorted((ROOT / "runtime" / "examples").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
            imports = {
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.Import, ast.ImportFrom))
                for alias in node.names
            }
            self.assertTrue(forbidden.isdisjoint(names | imports), (path, names | imports))

    def test_17_example_package_has_no_effect_capable_imports_or_calls(self):
        forbidden_imports = {
            "subprocess", "socket", "requests", "urllib", "kubernetes",
            "docker", "paramiko", "shlex", "pty", "os",
        }
        forbidden_calls = {
            "open", "connect", "send", "sendto", "bind", "listen",
            "system", "popen", "run", "call", "spawn",
        }
        for path in sorted((ROOT / "runtime" / "examples").glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
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

    def test_18_descriptor_is_immutable_and_deterministic(self):
        with self.assertRaises(FrozenInstanceError):
            E.workload_name = "changed"
        canonical_a = json.dumps(asdict(E), sort_keys=True, default=str)
        canonical_b = json.dumps(asdict(E), sort_keys=True, default=str)
        self.assertEqual(canonical_a, canonical_b)


if __name__ == "__main__":
    unittest.main(verbosity=2)
