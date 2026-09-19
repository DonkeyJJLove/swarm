"""E5 manifest security regression guard.

Static only: parses repository YAML and validates bounded security invariants.
It never contacts a Kubernetes cluster and never deploys resources.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
MUTATING_VERBS = {"create", "update", "patch", "delete", "deletecollection"}
PRIVILEGE_VERBS = {"escalate", "bind", "impersonate"}
ROLE_KINDS = {"Role", "ClusterRole"}
FORBIDDEN_CLUSTER_SCOPED_KINDS = {"ClusterRole", "ClusterRoleBinding"}


def repository_yaml_paths() -> list[Path]:
    paths = sorted({*ROOT.rglob("*.yaml"), *ROOT.rglob("*.yml")})
    return [
        path
        for path in paths
        if ".git" not in path.parts and ".github" not in path.parts
    ]


def load_yaml_documents(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as handle:
        docs = list(yaml.safe_load_all(handle))
    return [doc for doc in docs if isinstance(doc, dict)]


def kubernetes_documents() -> list[tuple[Path, dict]]:
    result: list[tuple[Path, dict]] = []
    for path in repository_yaml_paths():
        for doc in load_yaml_documents(path):
            if isinstance(doc.get("apiVersion"), str) and isinstance(doc.get("kind"), str):
                result.append((path, doc))
    return result


class ManifestSecurityGuardTests(unittest.TestCase):
    def test_all_targeted_yaml_parses(self):
        paths = repository_yaml_paths()
        self.assertTrue(paths, "no YAML files discovered")
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                load_yaml_documents(path)

    def test_rbac_has_no_wildcards_or_mutating_privilege_verbs(self):
        for path, doc in kubernetes_documents():
            kind = doc.get("kind")
            if kind in FORBIDDEN_CLUSTER_SCOPED_KINDS:
                self.fail(
                    f"{path.relative_to(ROOT)} introduces forbidden cluster-scoped RBAC kind {kind}"
                )
            if kind not in ROLE_KINDS:
                continue
            for index, rule in enumerate(doc.get("rules") or []):
                verbs = {str(v).lower() for v in (rule.get("verbs") or [])}
                resources = {str(v) for v in (rule.get("resources") or [])}
                api_groups = {str(v) for v in (rule.get("apiGroups") or [])}
                self.assertNotIn("*", verbs, f"{path.relative_to(ROOT)} rule {index}: wildcard verb")
                self.assertNotIn("*", resources, f"{path.relative_to(ROOT)} rule {index}: wildcard resource")
                self.assertNotIn("*", api_groups, f"{path.relative_to(ROOT)} rule {index}: wildcard apiGroup")
                self.assertFalse(
                    verbs & MUTATING_VERBS,
                    f"{path.relative_to(ROOT)} rule {index}: mutating verbs {sorted(verbs & MUTATING_VERBS)}",
                )
                self.assertFalse(
                    verbs & PRIVILEGE_VERBS,
                    f"{path.relative_to(ROOT)} rule {index}: privilege verbs {sorted(verbs & PRIVILEGE_VERBS)}",
                )

    def test_aggregator_role_is_exact_read_only_contract(self):
        roles = []
        for path, doc in kubernetes_documents():
            if doc.get("kind") != "Role":
                continue
            metadata = doc.get("metadata") or {}
            if metadata.get("name") == "aggregator-role":
                roles.append((path, doc))
        self.assertEqual(len(roles), 1, "aggregator-role must exist exactly once")
        path, role = roles[0]
        self.assertEqual(
            role.get("rules"),
            [{
                "apiGroups": [""],
                "resources": ["pods", "services"],
                "verbs": ["get", "list", "watch"],
            }],
            f"{path.relative_to(ROOT)}: aggregator-role drifted from qualified read-only contract",
        )

    def test_committed_secret_values_are_placeholders_only(self):
        secrets = [
            (path, doc)
            for path, doc in kubernetes_documents()
            if doc.get("kind") == "Secret"
        ]
        for path, secret in secrets:
            data = secret.get("data") or {}
            self.assertFalse(
                data,
                f"{path.relative_to(ROOT)}: committed Secret.data is not allowed by this guard",
            )
            string_data = secret.get("stringData") or {}
            for key, value in string_data.items():
                self.assertIsInstance(
                    value,
                    str,
                    f"{path.relative_to(ROOT)}: stringData.{key} must be a string placeholder",
                )
                self.assertTrue(
                    value.startswith("CHANGEME_"),
                    f"{path.relative_to(ROOT)}: stringData.{key} is not a CHANGEME_ placeholder",
                )

    def test_report_service_account_bindings(self):
        bindings = []
        for path, doc in kubernetes_documents():
            spec = doc.get("spec")
            if not isinstance(spec, dict):
                continue
            pod_spec = None
            if isinstance(spec.get("template"), dict):
                pod_spec = spec["template"].get("spec") or {}
            elif doc.get("kind") == "Pod":
                pod_spec = spec
            if isinstance(pod_spec, dict) and pod_spec.get("serviceAccountName"):
                bindings.append({
                    "path": path.relative_to(ROOT).as_posix(),
                    "kind": doc.get("kind"),
                    "name": (doc.get("metadata") or {}).get("name"),
                    "serviceAccountName": pod_spec.get("serviceAccountName"),
                })
        print("SERVICE_ACCOUNT_BINDINGS=" + json.dumps(bindings, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
