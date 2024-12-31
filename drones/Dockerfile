FROM python:3.11-slim

WORKDIR /app
COPY drone_logic.py /app/drone_logic.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV DRONE_ID="default_drone"
ENV AGGREGATOR_HOST="aggregator-service.laboratory-swarm.svc.cluster.local"
ENV AGGREGATOR_PORT="6000"

EXPOSE 7000

CMD ["python", "drone_logic.py"]
