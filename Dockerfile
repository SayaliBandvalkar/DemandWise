# ==============================================================================
# DemandWise - Enterprise Full-Stack Deployment Dockerfile
# Stage 1: Build React TypeScript Frontend
# Stage 2: High-Performance Python 3.12 FastAPI Server
# ==============================================================================

# --- Stage 1: Frontend Build ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package.json ./
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Production Application Runtime ---
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    SERVE_FRONTEND=true \
    DEBUG=false \
    PYTHONPATH="/app:/app/src"

# Install runtime utilities and OpenMP library for LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project configuration, documentation, source code, backend, and data
COPY README.md pyproject.toml ./
COPY src/ ./src/
COPY backend/ ./backend/
COPY data/ ./data/
COPY configs/ ./configs/
COPY artifacts/ ./artifacts/

# Install project package now that src/ and README.md are present
RUN pip install --no-cache-dir -e . --no-deps

# Copy built frontend distribution from Stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
