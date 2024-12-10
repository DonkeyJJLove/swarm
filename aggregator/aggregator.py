import socket
import threading

AGGREGATOR_PORT = 5001  # Port dla agregatora


def handle_message(data, addr):
    message = data.decode()
    print(f"Received from {addr}: {message}")
    # Tu możesz dodać logikę zapisu danych do bazy, przetwarzania, itp.


def run_aggregator():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", AGGREGATOR_PORT))
    print(f"Aggregator listening on port {AGGREGATOR_PORT}")

    while True:
        data, addr = sock.recvfrom(1024)
        threading.Thread(target=handle_message, args=(data, addr)).start()


if __name__ == "__main__":
    run_aggregator()
