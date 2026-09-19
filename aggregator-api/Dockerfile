FROM python:3.11-slim

WORKDIR /app
COPY aggregator_api.py /app/aggregator_api.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV DRONE_ID="default_drone"
ENV AGGREGATOR_HOST="aggregator-service.laboratory-swarm.svc.cluster.local"
ENV AGGREGATOR_PORT="5001"

EXPOSE 6001

CMD ["python", "aggregator_api.py"]
