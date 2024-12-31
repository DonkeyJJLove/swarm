import os
import socket
import time
import random
import uuid
import json

# Pobranie DRONE_NAME z zmiennej środowiskowej lub wygenerowanie unikalnej nazwy
DRONE_NAME = os.getenv("DRONE_ID", f"drone_{uuid.uuid4().hex[:8]}")
AGGREGATOR_HOST = os.getenv("AGGREGATOR_HOST", "aggregator-service.laboratory-swarm.svc.cluster.local")
AGGREGATOR_PORT = int(os.getenv("AGGREGATOR_PORT", "6000"))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

position = {"latitude": random.uniform(-90, 90), "longitude": random.uniform(-180, 180)}
battery_level = 100

while True:
    # Tworzenie wiadomości w formacie JSON
    data = {
        "drone_id": DRONE_NAME,
        "position": position,
        "battery_level": battery_level
    }
    message = json.dumps(data)
    try:
        # Wysyłanie danych do agregatora
        sock.sendto(message.encode(), (AGGREGATOR_HOST, AGGREGATOR_PORT))
        print(f"Drone {DRONE_NAME} published data: {data}")
    except Exception as e:
        print(f"Error sending data: {e}")

    # Symulacja obniżenia baterii
    battery_level = max(battery_level - random.randint(0, 5), 0)

    # Prosta symulacja ruchu
    position["latitude"] += random.uniform(-0.001, 0.001)
    position["longitude"] += random.uniform(-0.001, 0.001)

    time.sleep(5)
