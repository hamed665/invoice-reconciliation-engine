FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && useradd --uid 10001 --create-home appuser
COPY --chown=appuser:appuser . .
USER 10001
ENV HOST=0.0.0.0 DEMO_ONLY=true PYTHONDONTWRITEBYTECODE=1
CMD ["python", "server.py"]
