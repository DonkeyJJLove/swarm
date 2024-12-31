# ----------------------------------------------------------------------------
# Base Image: python:3.11-slim
# Maintainer: d2j3
# Version: 1.0
# Description: Docker image for the UDP data aggregator (aggregator.py)
# Application: data-aggregator
# ----------------------------------------------------------------------------

# Użycie oficjalnego lekkiego obrazu Pythona
FROM python:3.11-slim

# Metadane obrazu
LABEL org.opencontainers.image.title="Data Aggregator"
LABEL org.opencontainers.image.description="A lightweight UDP data aggregator application."
LABEL org.opencontainers.image.version="1.0"
LABEL org.opencontainers.image.authors="d2j3"
LABEL org.opencontainers.image.licenses="MIT"

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie zależności i ich instalacja
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Skopiowanie głównego pliku aplikacji
COPY aggregator.py /app/aggregator.py

ENV AGGREGATOR_PORT=6000
ENV AGGREGATOR_API_URL=http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data

EXPOSE 6000/udp

CMD ["python", "aggregator.py"]
