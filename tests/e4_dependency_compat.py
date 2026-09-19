"""Focused E4 compatibility probes for the PR #7 dependency refresh.

These tests exercise the affected Flask and Requests call paths without
external PostgreSQL, MQTT, Kubernetes, or network dependencies.
"""

from __future__ import annotations

import importlib.util
from importlib.metadata import version
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Cursor:
    def __init__(self, *, one=None, many=None):
        self._one = one
        self._many = many or []
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._many

    def close(self):
        return None


class _Connection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False

    def cursor(self, *args, **kwargs):
        return self._cursor

    def commit(self):
        self.committed = True

    def close(self):
        return None


class DependencyCompatibilityTests(unittest.TestCase):
    def test_expected_dependency_versions_are_installed(self):
        self.assertEqual(version("Flask"), "3.1.3")
        self.assertEqual(version("requests"), "2.33.0")

    def test_aggregator_api_flask_paths(self):
        mod = load_module("e4_aggregator_api", "aggregator-api/aggregator_api.py")

        write_cursor = _Cursor()
        write_conn = _Connection(write_cursor)
        mod.get_db_connection = lambda: write_conn

        client = mod.app.test_client()
        response = client.post(
            "/api/data",
            json={"drone_id": "d-1", "position": {"x": 1}, "battery_level": 85},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "success"})
        self.assertTrue(write_conn.committed)

        read_cursor = _Cursor(
            one={"position": {"x": 1}, "battery_level": 85}
        )
        mod.get_db_connection = lambda: _Connection(read_cursor)
        response = client.get("/api/drones/d-1/status")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"drone_id": "d-1", "position": {"x": 1}, "battery_level": 85},
        )

    def test_server_flask_data_path(self):
        mod = load_module("e4_server_app", "server/app.py")
        cursor = _Cursor(many=[("d-1", {"x": 1}, 85)])
        mod.get_db_connection = lambda: _Connection(cursor)

        client = mod.app.test_client()
        response = client.get("/server/data")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            [{"drone_id": "d-1", "position": {"x": 1}, "battery_level": 85}],
        )

    def test_mqtt_bridge_requests_path(self):
        mod = load_module(
            "e4_mqtt_bridge", "aggregator/mqtt_bridge/mqtt_bridge.py"
        )
        seen = {}

        class _Response:
            status_code = 200

        def fake_post(url, json):
            seen["url"] = url
            seen["json"] = json
            return _Response()

        mod.requests.post = fake_post

        class _Message:
            topic = "drone/positions"
            payload = b'{"drone_id":"d-1","position":{"x":1},"battery_level":85}'

        mod.on_message(None, None, _Message())
        self.assertEqual(seen["url"], mod.TARGET_API_URL)
        self.assertEqual(seen["json"]["drone_id"], "d-1")
        self.assertEqual(seen["json"]["battery_level"], 85)


if __name__ == "__main__":
    unittest.main()
