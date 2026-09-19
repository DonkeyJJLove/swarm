"""LION E4 PR10 ephemeral runtime proof controller.

Test-runtime only. This process never manages Docker, Compose, Kubernetes,
or host state. It talks only to the isolated services supplied by the harness.
"""

from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import psycopg2
import requests


POSTGRES_READY_TIMEOUT = 30.0
MQTT_READY_TIMEOUT = 20.0
AGGREGATOR_READY_TIMEOUT = 20.0
SERVER_READY_TIMEOUT = 20.0
MQTT_PUBLISH_TIMEOUT = 10.0
DB_PROPAGATION_TIMEOUT = 10.0
HTTP_REQUEST_TIMEOUT = 5.0
DB_QUERY_TIMEOUT = 5.0
TOTAL_RUNTIME_TIMEOUT = 120.0
MAX_RETRY_SLEEP = 1.0

REQUIRED_FAILURE_TAXONOMY = (
    "POSTGRES_START_FAILURE",
    "POSTGRES_SCHEMA_FAILURE",
    "MQTT_BROKER_START_FAILURE",
    "MQTT_CONNECT_FAILURE",
    "MQTT_PUBLISH_FAILURE",
    "MQTT_DELIVERY_FAILURE",
    "DUPLICATE_DELIVERY_FAILURE",
    "AGGREGATOR_START_FAILURE",
    "AGGREGATOR_HTTP_FAILURE",
    "DATABASE_CONNECT_FAILURE",
    "DATABASE_WRITE_FAILURE",
    "DATABASE_READBACK_FAILURE",
    "AGGREGATOR_READBACK_FAILURE",
    "SERVER_START_FAILURE",
    "SERVER_READBACK_FAILURE",
    "TIMEOUT",
    "HARNESS_INTERNAL_FAILURE",
)

PROBE_ID = "e4-runtime-probe-1"
PAYLOAD = {
    "drone_id": PROBE_ID,
    "position": {"x": 1, "y": 2},
    "battery_level": 85,
}


class ProbeFailure(RuntimeError):
    def __init__(self, classification: str, detail: str):
        super().__init__(detail)
        self.classification = classification
        self.detail = detail


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def bounded_sleep(deadline: float, seconds: float = 0.5) -> None:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise ProbeFailure("TIMEOUT", "total runtime deadline exceeded")
    time.sleep(min(seconds, MAX_RETRY_SLEEP, remaining))


def connect_db(dsn: str, timeout: float):
    return psycopg2.connect(
        dsn,
        connect_timeout=max(1, int(timeout)),
        options=f"-c statement_timeout={int(DB_QUERY_TIMEOUT * 1000)}",
    )


def wait_postgres(dsn: str, deadline: float, receipt: dict) -> None:
    local_deadline = min(deadline, time.monotonic() + POSTGRES_READY_TIMEOUT)
    last_error = "not-ready"
    while time.monotonic() < local_deadline:
        try:
            conn = connect_db(dsn, 2)
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT to_regclass('public.drone_data')")
                    table = cur.fetchone()[0]
                    if table == "drone_data":
                        receipt["readiness"]["postgres"] = True
                        return
                    last_error = "drone_data-missing"
            finally:
                conn.close()
        except psycopg2.errors.QueryCanceled:
            raise ProbeFailure("TIMEOUT", "db_statement_timeout") from None
        except Exception as exc:
            last_error = type(exc).__name__
        bounded_sleep(deadline)
    classification = (
        "POSTGRES_SCHEMA_FAILURE"
        if last_error == "drone_data-missing"
        else "POSTGRES_START_FAILURE"
    )
    raise ProbeFailure(classification, last_error)


def wait_http_404(url: str, deadline: float, receipt: dict) -> None:
    local_deadline = min(deadline, time.monotonic() + AGGREGATOR_READY_TIMEOUT)
    last_status = None
    while time.monotonic() < local_deadline:
        try:
            response = requests.get(url, timeout=HTTP_REQUEST_TIMEOUT)
            last_status = response.status_code
            if response.status_code == 404:
                receipt["readiness"]["aggregator-api"] = True
                return
        except requests.RequestException:
            pass
        bounded_sleep(deadline)
    raise ProbeFailure("AGGREGATOR_START_FAILURE", f"last_status={last_status}")


def wait_server_empty(url: str, deadline: float, receipt: dict) -> None:
    local_deadline = min(deadline, time.monotonic() + SERVER_READY_TIMEOUT)
    last_status = None
    while time.monotonic() < local_deadline:
        try:
            response = requests.get(url, timeout=HTTP_REQUEST_TIMEOUT)
            last_status = response.status_code
            if response.status_code == 200 and response.json() == []:
                receipt["readiness"]["server"] = True
                return
        except (requests.RequestException, ValueError):
            pass
        bounded_sleep(deadline)
    raise ProbeFailure("SERVER_START_FAILURE", f"last_status={last_status}")


def wait_mqtt_and_bridge(
    broker: str,
    port: int,
    topic: str,
    deadline: float,
    receipt: dict,
):
    broker_deadline = min(deadline, time.monotonic() + MQTT_READY_TIMEOUT)
    broker_reachable = False
    while time.monotonic() < broker_deadline:
        try:
            sock = socket.create_connection((broker, port), timeout=1.0)
            sock.close()
            broker_reachable = True
            break
        except OSError:
            bounded_sleep(deadline, 0.2)

    if not broker_reachable:
        raise ProbeFailure(
            "MQTT_BROKER_START_FAILURE",
            "broker_tcp_unavailable",
        )

    connected = threading.Event()
    subscription_count_ready = threading.Event()
    connection_rc = {"value": None}

    client = mqtt.Client(client_id="e4-runtime-probe-controller", clean_session=True)

    def on_connect(client_obj, userdata, flags, rc):
        connection_rc["value"] = rc
        if rc == 0:
            connected.set()
            client_obj.subscribe("$SYS/broker/subscriptions/count", qos=0)

    def on_message(client_obj, userdata, message):
        if message.topic != "$SYS/broker/subscriptions/count":
            return
        try:
            count = int(message.payload.decode("ascii").strip())
        except (ValueError, UnicodeDecodeError):
            return
        # Isolated broker: one SYS subscription belongs to this probe and
        # another subscription must belong to mqtt_bridge on drone/positions.
        if count >= 2:
            subscription_count_ready.set()

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(broker, port, keepalive=10)
        client.loop_start()
    except Exception as exc:
        raise ProbeFailure("MQTT_CONNECT_FAILURE", type(exc).__name__) from None

    local_deadline = min(deadline, time.monotonic() + MQTT_READY_TIMEOUT)
    try:
        while time.monotonic() < local_deadline and not connected.is_set():
            bounded_sleep(deadline, 0.2)
        if not connected.is_set() or connection_rc["value"] != 0:
            raise ProbeFailure(
                "MQTT_CONNECT_FAILURE",
                f"connect_rc={connection_rc['value']}",
            )

        while (
            time.monotonic() < local_deadline
            and not subscription_count_ready.is_set()
        ):
            bounded_sleep(deadline, 0.2)

        if not subscription_count_ready.is_set():
            raise ProbeFailure(
                "MQTT_CONNECT_FAILURE",
                "mqtt_bridge subscription readiness not observed",
            )

        receipt["readiness"]["mqtt"] = True
        receipt["mqtt"]["connected"] = True
        receipt["mqtt"]["subscribed"] = True

        # QoS 1 is a harness-only choice so publish completion is explicit.
        info = client.publish(
            topic,
            payload=json.dumps(PAYLOAD, separators=(",", ":")),
            qos=1,
            retain=False,
        )
        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            raise ProbeFailure("MQTT_PUBLISH_FAILURE", f"publish_rc={info.rc}")

        info.wait_for_publish(timeout=MQTT_PUBLISH_TIMEOUT)
        if not info.is_published():
            raise ProbeFailure("MQTT_PUBLISH_FAILURE", "publish timeout")

        receipt["mqtt"]["published"] = True
        receipt["mqtt"]["publish_ack_or_completion"] = True
        return client
    except Exception:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception:
            pass
        raise


def wait_db_row(dsn: str, deadline: float, receipt: dict) -> dict:
    local_deadline = min(deadline, time.monotonic() + DB_PROPAGATION_TIMEOUT)
    last_count = 0
    while time.monotonic() < local_deadline:
        try:
            conn = connect_db(dsn, 2)
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT drone_id, position, battery_level, timestamp
                        FROM drone_data
                        WHERE drone_id = %s
                        ORDER BY timestamp DESC
                        """,
                        (PROBE_ID,),
                    )
                    rows = cur.fetchall()
            finally:
                conn.close()
        except psycopg2.errors.QueryCanceled:
            raise ProbeFailure("TIMEOUT", "db_statement_timeout") from None
        except Exception as exc:
            raise ProbeFailure(
                "DATABASE_READBACK_FAILURE", type(exc).__name__
            ) from None

        last_count = len(rows)
        if last_count > 1:
            raise ProbeFailure(
                "DUPLICATE_DELIVERY_FAILURE", f"probe_row_count={last_count}"
            )
        if last_count == 1:
            drone_id, position, battery_level, timestamp = rows[0]
            if (
                drone_id != PROBE_ID
                or position != PAYLOAD["position"]
                or battery_level != PAYLOAD["battery_level"]
                or timestamp is None
            ):
                raise ProbeFailure(
                    "DATABASE_READBACK_FAILURE", "probe row semantic mismatch"
                )
            row = {
                "drone_id": drone_id,
                "position": position,
                "battery_level": battery_level,
                "timestamp_present": timestamp is not None,
            }
            receipt["database"] = {
                "probe_row_count": 1,
                "probe_row": row,
                "timestamp_present": True,
            }
            return row
        bounded_sleep(deadline)

    receipt["database"]["probe_row_count"] = last_count
    raise ProbeFailure("MQTT_DELIVERY_FAILURE", "probe row not persisted")


def assert_aggregator(base_url: str, deadline: float, receipt: dict) -> None:
    if time.monotonic() >= deadline:
        raise ProbeFailure("TIMEOUT", "before aggregator readback")
    try:
        response = requests.get(
            f"{base_url}/api/drones/{PROBE_ID}/status",
            timeout=HTTP_REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise ProbeFailure(
            "AGGREGATOR_HTTP_FAILURE", type(exc).__name__
        ) from None

    expected = PAYLOAD
    semantic_match = response.status_code == 200 and response.json() == expected
    receipt["aggregator_readback"] = {
        "http_status": response.status_code,
        "semantic_match": semantic_match,
    }
    if not semantic_match:
        raise ProbeFailure(
            "AGGREGATOR_READBACK_FAILURE",
            f"http_status={response.status_code}",
        )


def assert_server(base_url: str, deadline: float, receipt: dict) -> None:
    if time.monotonic() >= deadline:
        raise ProbeFailure("TIMEOUT", "before server readback")
    try:
        response = requests.get(
            f"{base_url}/server/data",
            timeout=HTTP_REQUEST_TIMEOUT,
        )
        body = response.json()
    except requests.RequestException as exc:
        raise ProbeFailure("SERVER_READBACK_FAILURE", type(exc).__name__) from None
    except ValueError:
        raise ProbeFailure("SERVER_READBACK_FAILURE", "invalid JSON") from None

    expected_row = {
        "drone_id": PROBE_ID,
        "position": PAYLOAD["position"],
        "battery_level": PAYLOAD["battery_level"],
    }
    semantic_match = response.status_code == 200 and body == [expected_row]
    receipt["server_readback"] = {
        "http_status": response.status_code,
        "semantic_match": semantic_match,
    }
    if not semantic_match:
        raise ProbeFailure(
            "SERVER_READBACK_FAILURE",
            f"http_status={response.status_code}",
        )


def main() -> int:
    started_wall = utc_now()
    started_monotonic = time.monotonic()
    deadline = started_monotonic + TOTAL_RUNTIME_TIMEOUT

    receipt = {
        "schema_version": "lion-e4-runtime-proof-v1",
        "exact_head": os.getenv("EXPECTED_HEAD", "UNKNOWN"),
        "started_at": started_wall,
        "completed_at": None,
        "duration_ms": None,
        "readiness": {
            "postgres": False,
            "mqtt": False,
            "aggregator-api": False,
            "server": False,
        },
        "mqtt": {
            "connected": False,
            "subscribed": False,
            "published": False,
            "publish_ack_or_completion": False,
        },
        "database": {
            "probe_row_count": None,
            "probe_row": None,
            "timestamp_present": False,
        },
        "aggregator_readback": {
            "http_status": None,
            "semantic_match": False,
        },
        "server_readback": {
            "http_status": None,
            "semantic_match": False,
        },
        "final_result": "FAIL",
        "failure_classification": "HARNESS_INTERNAL_FAILURE",
    }

    dsn = os.environ["DATABASE_URL"]
    broker = os.getenv("MQTT_BROKER", "mqtt-broker")
    port = int(os.getenv("MQTT_PORT", "1883"))
    topic = os.getenv("MQTT_TOPIC", "drone/positions")
    aggregator_url = os.getenv("AGGREGATOR_URL", "http://aggregator-api:6001")
    server_url = os.getenv("SERVER_URL", "http://server:8000")

    mqtt_client = None
    try:
        wait_postgres(dsn, deadline, receipt)
        wait_http_404(
            f"{aggregator_url}/__e4_runtime_readiness__",
            deadline,
            receipt,
        )
        wait_server_empty(f"{server_url}/server/data", deadline, receipt)
        mqtt_client = wait_mqtt_and_bridge(
            broker, port, topic, deadline, receipt
        )
        wait_db_row(dsn, deadline, receipt)
        assert_aggregator(aggregator_url, deadline, receipt)
        assert_server(server_url, deadline, receipt)
        receipt["final_result"] = "PASS"
        receipt["failure_classification"] = None
        return_code = 0
    except ProbeFailure as exc:
        receipt["failure_classification"] = exc.classification
        return_code = 2
    except Exception:
        receipt["failure_classification"] = "HARNESS_INTERNAL_FAILURE"
        return_code = 3
    finally:
        if mqtt_client is not None:
            try:
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
            except Exception:
                pass
        receipt["completed_at"] = utc_now()
        receipt["duration_ms"] = int(
            (time.monotonic() - started_monotonic) * 1000
        )
        print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))

    return return_code


if __name__ == "__main__":
    sys.exit(main())
