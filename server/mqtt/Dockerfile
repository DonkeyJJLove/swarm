# mqtt_aggregator/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY mqtt/mqtt_aggregator.py /app/mqtt_aggregator.py

RUN pip install paho-mqtt

ENV MQTT_BROKER=mqtt-broker
ENV MQTT_PORT=1883

CMD ["python", "mqtt_aggregator.py"]
