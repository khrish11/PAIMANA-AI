FROM python:3.11-slim

# Install system dependencies for LightGBM (OpenMP runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Add project root to PYTHONPATH for imports
ENV PYTHONPATH=/app:/data

CMD ["python", "-m", "alembic", "upgrade", "head"]
