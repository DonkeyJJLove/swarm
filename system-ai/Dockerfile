FROM python:3.11-slim

WORKDIR /app

COPY model.joblib /app/model.joblib
COPY ai_service.py /app/ai_service.py
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

ENV MODEL_PATH=/app/model.joblib

CMD ["python", "ai_service.py"]
