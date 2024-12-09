FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY mqtt_aggregator.py /app/mqtt_aggregator.py

ENV MQTT_BROKER=mqtt-broker
ENV MQTT_PORT=1883

CMD ["python", "mqtt_aggregator.py"]
