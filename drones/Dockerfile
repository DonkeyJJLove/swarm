FROM python:3.11-slim

WORKDIR /app

# Najpierw kopiujemy requirements.txt
COPY requirements.txt /app/requirements.txt

# Następnie instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Potem kopiujemy kod aplikacji
COPY mqtt_aggregator.py /app/mqtt_aggregator.py

ENV MQTT_BROKER=mqtt-broker
ENV MQTT_PORT=1883

CMD ["python", "mqtt_aggregator.py"]
