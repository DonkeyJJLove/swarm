import os
import paho.mqtt.client as mqtt

# Zmienne środowiskowe:
# - MQTT_BROKER: nazwa hosta (Service w K8s) brokera, domyślnie "mqtt-broker"
# - MQTT_PORT: numer portu (zwykle 1883)
# - MQTT_TOPIC: topik do subskrypcji, np. "drone/positions"

MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt-broker")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
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

    # W tym miejscu można dodać logikę:
    # - Forward do aggregator UDP (wysyłka na aggregator-service:5001)
    # - Zapis do bazy / innego API
    # - Filtry anomalii, itp.


if __name__ == "__main__":
    print("[mqtt_bridge] Starting up MQTT bridge...")

    # Tworzymy klienta MQTT (bez uwierzytelniania, można dodać username_pw_set())
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # Łączymy się z brokerem
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        # Uruchamiamy pętlę obsługi wiadomości (blokuje w nieskończoność)
        client.loop_forever()
    except Exception as e:
        print(f"[mqtt_bridge] Fatal error: {e}")
