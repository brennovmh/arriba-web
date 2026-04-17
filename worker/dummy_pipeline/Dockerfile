FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir pillow

COPY run_pipeline.py /app/run_pipeline.py

ENTRYPOINT ["python", "/app/run_pipeline.py"]
