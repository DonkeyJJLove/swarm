#!/usr/bin/env python3
import subprocess
import sys

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas wykonywania polecenia: {e}", file=sys.stderr)

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
        choice = input("Wybierz opcję (1-6): ")

        if choice == '1':
            url = input("Podaj URL do sprawdzenia: ")
            run_command(f"curl -I {url}")
        elif choice == '2':
            target = input("Podaj adres IP lub domenę do zeskanowania: ")
            run_command(f"nmap -Pn {target}")
        elif choice == '3':
            server = input("Podaj adres serwera iperf3: ")
            run_command(f"iperf3 -c {server}")
        elif choice == '4':
            interface = input("Podaj interfejs sieciowy (np. eth0): ")
            filename = input("Podaj nazwę pliku do zapisania przechwyconych pakietów: ")
            run_command(f"tcpdump -i {interface} -w /captures/{filename}")
        elif choice == '5':
            target = input("Podaj URL do zeskanowania za pomocą nikto: ")
            run_command(f"nikto -h {target}")
        elif choice == '6':
            print("Zamykanie KubeDiag Toolkit.")
            break
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")

if __name__ == "__main__":
    main()
