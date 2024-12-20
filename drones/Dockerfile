FROM python:3.11-slim

WORKDIR /app
COPY drone_logic.py /app/drone_logic.py

# Instalacja zależności, jeśli są potrzebne (odkomentuj i dostosuj)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt


ENV DRONE_NAME="default_drone"
ENV DRONE_PORT="5000"

CMD ["python", "drone_logic.py"]