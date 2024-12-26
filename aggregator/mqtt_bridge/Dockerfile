FROM python:3.11-slim

WORKDIR /app

# Skopiowanie pliku requirements.txt i instalacja zależności
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Skopiowanie głównego skryptu mostka MQTT
COPY mqtt_bridge.py /app/mqtt_bridge.py

# Zmienne środowiskowe sterujące zachowaniem mostka
ENV MQTT_BROKER=mqtt-broker
ENV MQTT_PORT=1883
ENV MQTT_TOPIC=drone/positions

# Domyślna komenda
CMD ["python", "mqtt_bridge.py"]
