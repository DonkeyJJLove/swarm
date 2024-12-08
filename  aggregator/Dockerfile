# aggregator/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY aggregator.py /app/aggregator.py

# Instalacja zależności, jeśli są potrzebne
# RUN pip install <pakiety>

ENV AGGREGATOR_PORT=5001

CMD ["python", "aggregator.py"]
