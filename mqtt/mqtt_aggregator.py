import os
import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe("drone/positions")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    message = msg.payload.decode()
    print(f"Received: {message}")
    # Tu możesz dodać logikę zapisu danych do bazy, przetwarzania, itp.


client = mqtt.Client()  # Możesz dodać identyfikator klienta, jeśli potrzebujesz
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
