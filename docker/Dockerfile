FROM python:3.11-slim

WORKDIR /app
COPY drone_logic.py /app/drone_logic.py

# Jeśli potrzebujesz dodatkowych zależności:
# RUN pip install <pakiety>

ENV DRONE_NAME="default_drone"
ENV DRONE_PORT="5000"

CMD ["python", "drone_logic.py"]
