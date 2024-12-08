FROM python:3.11-slim

WORKDIR /app
COPY aggregator_api.py /app/aggregator_api.py

RUN pip install flask

ENV FLASK_APP=aggregator_api.py

CMD ["python", "aggregator_api.py"]
