#!/usr/bin/env python3
import ipaddress
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


_HOST_RE = re.compile(
    r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"
)
_INTERFACE_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,64}$")
_CAPTURE_RE = re.compile(r"^[A-Za-z0-9_.-]{1,128}$")


def run_command(argv):
    """Run a pre-structured command without invoking a shell."""
    try:
        result = subprocess.run(
            argv,
            shell=False,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except FileNotFoundError:
        print(f"Brak wymaganego narzędzia: {argv[0]}", file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        print(f"Błąd podczas wykonywania polecenia: {exc}", file=sys.stderr)
        if exc.stderr:
            print(exc.stderr, file=sys.stderr)


def validate_host(value):
    value = value.strip()
    try:
        ipaddress.ip_address(value)
        return value
    except ValueError:
        pass

    if _HOST_RE.fullmatch(value):
        return value
    raise ValueError("Nieprawidłowy adres IP lub nazwa hosta.")


def validate_http_url(value):
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Dozwolone są wyłącznie pełne adresy http:// lub https://.")
    # Reject credentials and control characters in a diagnostic target.
    if parsed.username or parsed.password or any(ord(ch) < 32 for ch in value):
        raise ValueError("URL zawiera niedozwolone elementy.")
    return value


def validate_interface(value):
    value = value.strip()
    if not _INTERFACE_RE.fullmatch(value):
        raise ValueError("Nieprawidłowa nazwa interfejsu.")
    return value


def validate_capture_name(value):
    value = Path(value.strip()).name
    if not _CAPTURE_RE.fullmatch(value) or value in {".", ".."}:
        raise ValueError("Nieprawidłowa nazwa pliku capture.")
    if not value.endswith(".pcap"):
        value += ".pcap"
    return value


def prompt_validated(prompt, validator):
    raw = input(prompt)
    try:
        return validator(raw)
    except ValueError as exc:
        print(f"Błąd wejścia: {exc}", file=sys.stderr)
        return None


def main():
    print("KubeDiag Toolkit - Prosty interfejs do uruchamiania narzędzi diagnostycznych")
    while True:
        print("\nDostępne opcje:")
        print("1. Sprawdzenie usługi HTTP za pomocą curl")
        print("2. Skanowanie portów za pomocą nmap")
        print("3. Testowanie przepustowości sieci za pomocą iperf3")
        print("4. Przechwytywanie ruchu sieciowego za pomocą tcpdump")
        print("5. Skanowanie podatności HTTP za pomocą nikto")
        print("6. Wyjście")
        choice = input("Wybierz opcję (1-6): ").strip()

        if choice == "1":
            url = prompt_validated("Podaj URL do sprawdzenia: ", validate_http_url)
            if url:
                run_command(["curl", "-I", "--", url])
        elif choice == "2":
            target = prompt_validated("Podaj adres IP lub domenę do zeskanowania: ", validate_host)
            if target:
                run_command(["nmap", "-Pn", "--", target])
        elif choice == "3":
            server = prompt_validated("Podaj adres serwera iperf3: ", validate_host)
            if server:
                run_command(["iperf3", "-c", server])
        elif choice == "4":
            interface = prompt_validated(
                "Podaj interfejs sieciowy (np. eth0): ", validate_interface
            )
            filename = prompt_validated(
                "Podaj nazwę pliku do zapisania przechwyconych pakietów: ",
                validate_capture_name,
            )
            if interface and filename:
                capture_path = str(Path("/captures") / filename)
                run_command(["tcpdump", "-i", interface, "-w", capture_path])
        elif choice == "5":
            target = prompt_validated(
                "Podaj URL do zeskanowania za pomocą nikto: ", validate_http_url
            )
            if target:
                run_command(["nikto", "-h", target])
        elif choice == "6":
            print("Zamykanie KubeDiag Toolkit.")
            break
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")


if __name__ == "__main__":
    main()
