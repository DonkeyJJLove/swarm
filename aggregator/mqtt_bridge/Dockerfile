FROM python:3.11-slim

WORKDIR /app

COPY mqtt_bridge.py /app/mqtt_bridge.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV MQTT_BROKER=mqtt-broker.laboratory-swarm.svc.cluster.local
ENV MQTT_PORT=1883
ENV TARGET_API_URL=http://aggregator-api-service.laboratory-swarm.svc.cluster.local:6001/api/data
ENV MQTT_TOPIC=drone/positions

CMD ["python", "mqtt_bridge.py"]
