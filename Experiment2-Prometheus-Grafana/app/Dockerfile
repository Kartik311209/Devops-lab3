FROM python:3.11-slim

# DevOps Lab 3 | Student: Kartik Kumar | Roll: 2301730205
LABEL maintainer="kartikjangra5366@gmail.com"
LABEL student="Kartik Kumar"
LABEL roll="2301730205"
LABEL project="devops-lab3"

WORKDIR /app

COPY app.py .

EXPOSE 8080

ENV PORT=8080
ENV STUDENT_NAME="Kartik Kumar"
ENV ROLL_NUMBER="2301730205"

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

CMD ["python3", "app.py"]

