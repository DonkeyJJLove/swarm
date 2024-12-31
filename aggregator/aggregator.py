import socket
import threading
import os
import json
import requests

# Odczyt portu z zmiennej środowiskowej AGGREGATOR_PORT (domyślnie 6000).
AGGREGATOR_PORT = int(os.getenv("AGGREGATOR_PORT", "6000"))
AGGREGATOR_API_URL = os.getenv("AGGREGATOR_API_URL",
                               "http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data")


def handle_message(data, addr):
    """
    Funkcja obsługująca każde odebrane pakiety UDP w osobnym wątku.

    :param data: surowe dane z gniazda socket
    :param addr: krotka (ip, port) nadawcy
    """
    try:
        # Dekodowanie w trybie 'replace' – nie przerywaj w razie błędów znaków
        message = data.decode(errors='replace')
        print(f"[aggregator] Received from {addr}: {message}")

        # Przekazywanie danych do Aggregator API
        data_json = json.loads(message)
        response = requests.post(AGGREGATOR_API_URL, json=data_json)
        if response.status_code == 200:
            print("[aggregator] Data successfully sent to Aggregator API.")
        else:
            print(f"[aggregator] Failed to send data to Aggregator API: {response.status_code}")
    except Exception as e:
        print(f"[aggregator] Error processing message: {e}")


def run_aggregator():
    """
    Główna pętla nasłuchu. Tworzy gniazdo UDP i odbiera pakiety na porcie AGGREGATOR_PORT.
    Każda odebrana wiadomość jest przekazywana do handle_message() w osobnym wątku.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", AGGREGATOR_PORT))
    print(f"[aggregator] Listening on port {AGGREGATOR_PORT} (UDP)")

    while True:
        data, addr = sock.recvfrom(1024)
        # Każdy pakiet obsługujemy w osobnym wątku, by nie blokować pętli nasłuchu.
        threading.Thread(
            target=handle_message,
            args=(data, addr),
            daemon=True
        ).start()


if __name__ == "__main__":
    run_aggregator()
