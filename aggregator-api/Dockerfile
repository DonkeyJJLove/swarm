FROM python:3.11-slim

WORKDIR /app
COPY aggregator_api/aggregator_api.py /app/aggregator_api.py

# Instalacja zależności, jeśli są potrzebne (odkomentuj i dostosuj)
COPY aggregator/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "aggregator_api.py"]
