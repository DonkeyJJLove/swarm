import os
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}", flush=True)
        client.subscribe("drone/positions")
    else:
        print(f"Failed to connect, return code {rc}", flush=True)

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received: {message}", flush=True)

print("Starting mqtt_aggregator...", flush=True)

client = mqtt.Client(client_id="mqtt_aggregator_client", protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

try:
    print("Attempting to connect to the broker...", flush=True)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print("Connection initiated, entering loop_forever...", flush=True)
    client.loop_forever()
except Exception as e:
    print(f"Connection failed: {e}", flush=True)

print(f"MQTT_BROKER: {MQTT_BROKER}, MQTT_PORT: {MQTT_PORT}", flush=True)
