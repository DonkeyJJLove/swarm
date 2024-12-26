FROM python:3.11-slim

# Metadane o obrazie (opcjonalne, ale przydatne)
LABEL maintainer="d2j3"
LABEL version="1.0"
LABEL description="Obraz agregatora danych (UDP) - aggregator.py"
LABEL application="data-aggregator"

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie pliku requirements.txt i instalacja zależności
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Skopiowanie głównego pliku aggregator.py
COPY aggregator.py /app/aggregator.py

# Ustawianie zmiennej środowiskowej z domyślną wartością portu
ENV AGGREGATOR_PORT=5001

# Otwieranie portu (informacyjne; w K8s i tak używamy Service)
EXPOSE ${AGGREGATOR_PORT}/udp

# Główna komenda
CMD ["python", "aggregator.py"]
