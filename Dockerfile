FROM node:22-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
COPY examples/demo_grid.json /app/examples/demo_grid.json
RUN npm run build

FROM python:3.12-slim-bookworm

ARG GIT_COMMIT=""
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ALLOW_LEGACY_FRONTEND=0 \
    APP_VERSION=0.2.0 \
    GIT_COMMIT=${GIT_COMMIT}

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py smt_engine.py heuristic_engine.py vision.py ./
COPY models ./models
COPY templates ./templates
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD ["python", "-c", "import json, urllib.request; data=json.load(urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)); assert data['status'] == 'ok'"]

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
