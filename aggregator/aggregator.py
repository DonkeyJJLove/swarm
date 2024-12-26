import socket
import threading
import os

# Odczyt portu z zmiennej środowiskowej AGGREGATOR_PORT (domyślnie 5001).
AGGREGATOR_PORT = int(os.getenv("AGGREGATOR_PORT", "5001"))

def handle_message(data, addr):
    """
    Funkcja obsługująca każde odebrane pakiety UDP w osobnym wątku.

    :param data: surowe dane z gniazda socket
    :param addr: krotka (ip, port) nadawcy
    """
    # Dekodowanie w trybie 'replace' – nie przerywaj w razie błędów znaków
    message = data.decode(errors='replace')
    print(f"[aggregator] Received from {addr}: {message}")

    # W tym miejscu można:
    # 1. Zapisać dane do bazy
    # 2. Przetworzyć / zanalizować dane
    # 3. Wysłać je do innego serwisu (np. aggregator-api) - requests.post(...)
    # 4. Wprowadzić logikę walidacji lub weryfikacji (np. JSON vs surowy tekst)
    # 5. Obserwować potencjalne anomalie, logować w systemie SIEM

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
