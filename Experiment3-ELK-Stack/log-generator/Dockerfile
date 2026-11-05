FROM python:3.11-slim

LABEL maintainer="kartikjangra5366@gmail.com"
LABEL student="Kartik Kumar"
LABEL roll="2301730205"

WORKDIR /app

COPY log_generator.py .

RUN mkdir -p /app/logs

ENV LOG_DIR=/app/logs
ENV LOG_INTERVAL=0.5

CMD ["python3", "-u", "log_generator.py"]

