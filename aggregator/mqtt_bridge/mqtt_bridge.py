import os
import paho.mqtt.client as mqtt
import requests
import json

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-broker.laboratory-swarm.svc.cluster.local")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
TARGET_API_URL = os.getenv("TARGET_API_URL",
                           "http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "drone/positions")


def on_connect(client, userdata, flags, rc):
    """
    Funkcja wywoływana po próbie połączenia z brokerem MQTT.
    rc == 0 oznacza sukces; wówczas subskrybujemy wskazany topik.
    """
    if rc == 0:
        print(f"[mqtt_bridge] Connected to {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"[mqtt_bridge] Subscribed to topic '{MQTT_TOPIC}'")
    else:
        print(f"[mqtt_bridge] Connection failed (rc={rc})")


def on_message(client, userdata, msg):
    """
    Funkcja wywoływana dla każdej wiadomości otrzymanej z zasubskrybowanego topiku.
    """
    payload_str = msg.payload.decode(errors='replace')
    print(f"[mqtt_bridge] Received on {msg.topic}: {payload_str}")

    # Przekazywanie danych do Aggregator API
    try:
        data = json.loads(payload_str)
        response = requests.post(TARGET_API_URL, json=data)
        if response.status_code == 200:
            print("[mqtt_bridge] Successfully sent data to Aggregator API.")
        else:
            print(f"[mqtt_bridge] Failed to send data to Aggregator API: {response.status_code}")
    except Exception as e:
        print(f"[mqtt_bridge] Error sending data to Aggregator API: {e}")


if __name__ == "__main__":
    print("[mqtt_bridge] Starting up MQTT bridge...")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print(f"[mqtt_bridge] Fatal error: {e}")
