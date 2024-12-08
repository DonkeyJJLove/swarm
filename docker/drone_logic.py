import os
import socket
import time
import random

DRONE_NAME = os.getenv("DRONE_NAME", f"drone_{random.randint(1000, 9999)}")
DRONE_PORT = int(os.getenv("DRONE_PORT", "5000"))
DISCOVERY_HOST = "drone-service"  # DNS usługi, która będzie headless
DISCOVERY_PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", DRONE_PORT))

position = [random.randint(0, 100), random.randint(0, 100)]

while True:
    # Wysyłanie pozycji do DISCOVERY_HOST (headless service)
    message = f"{DRONE_NAME} at position {position[0]}, {position[1]}"
    try:
        sock.sendto(message.encode(), (DISCOVERY_HOST, DISCOVERY_PORT))
    except Exception as e:
        pass  # może się nie powieść, jeśli nie ma jeszcze innych podów

    # Odbiór wiadomości od innych
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
