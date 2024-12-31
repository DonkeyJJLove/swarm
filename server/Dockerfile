FROM python:3.11-slim

WORKDIR /app
COPY app.py /app/app.py
COPY visualization.py /app/visualization.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV DATABASE_URL=postgresql://user:password@postgresql.laboratory-swarm.svc.cluster.local:5432/drone_db

EXPOSE 8000

CMD ["python", "app.py"]
