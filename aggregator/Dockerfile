#aggregator/Dockerfile
FROM python:3.11-slim

# Ustawienie metadanych obrazu
LABEL maintainer="Twoje Imię <twoj.email@domena.com>"
LABEL version="1.0"
LABEL description="Obraz agregatora danych, który uruchamia skrypt aggregator.py"
LABEL application="data-aggregator"

# Ustawienie katalogu roboczego
WORKDIR /app

# Skopiowanie pliku skryptu do katalogu roboczego
COPY aggregator/aggregator.py /app/aggregator.py

# Instalacja zależności, jeśli są potrzebne (odkomentuj i dostosuj)
COPY aggregator/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Zdefiniowanie zmiennych środowiskowych z opisem
ENV AGGREGATOR_PORT=5001

# Otworzenie portu dla aplikacji
EXPOSE ${AGGREGATOR_PORT}

# Domyślne polecenie do uruchomienia aplikacji
CMD ["python", "aggregator.py"]
