import os
import socket
import time
import random
import uuid

# Pobranie DRONE_NAME z zmiennej środowiskowej lub wygenerowanie unikalnej nazwy
DRONE_NAME = os.getenv("DRONE_NAME", f"drone_{uuid.uuid4().hex[:8]}")
DRONE_PORT = int(os.getenv("DRONE_PORT", "5000"))

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

position = [random.randint(0, 100), random.randint(0, 100)]

while True:
    # Tworzenie wiadomości
    message = f"{DRONE_NAME} at position {position[0]}, {position[1]}"
    try:
        # Wysyłanie danych do agregatora
        sock.sendto(message.encode(), (AGGREGATOR_HOST, AGGREGATOR_PORT))
    except Exception as e:
        print(f"Error sending data: {e}")

    # Odbiór wiadomości od innych (opcjonalne)
    sock.settimeout(1.0)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"[{DRONE_NAME}] received from {addr}: {data.decode()}")
    except socket.timeout:
        pass

    # Prosta symulacja ruchu
    position[0] += random.randint(-1, 1)
    position[1] += random.randint(-1, 1)
    time.sleep(5)
