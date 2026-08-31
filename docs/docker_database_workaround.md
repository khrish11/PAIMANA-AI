# PostgreSQL Authentication Workaround for Windows

## Problem
When connecting to PostgreSQL from the host machine on Windows, the connection fails with:
```
FATAL: password authentication failed for user "paimana"
```

This occurs due to authentication method incompatibilities between:
- PostgreSQL versions (14, 15, 16) which default to `scram-sha-256` authentication
- `psycopg2-binary` which uses MD5 authentication
- Docker port mapping which can cause IPv6/IPv4 resolution issues

## Solution: Docker Network Connectivity

The workaround is to run database operations (migrations, API) within the Docker network where authentication works correctly.

### Steps

1. **Start PostgreSQL via Docker Compose:**
   ```bash
   docker compose -f infra/docker-compose.yml up -d db
   ```

2. **Run migrations via Docker network:**
   ```bash
   docker compose -f infra/docker-compose.yml up backend
   ```
   
   This runs the backend container with `DATABASE_URL=postgresql+psycopg2://paimana:paimanapass@db:5432/paimana_ai` where `db` is the Docker network hostname.

3. **Run API server via Docker network:**
   ```bash
   docker compose -f infra/docker-compose.yml up api
   ```

### Configuration

**`infra/docker-compose.yml`** includes:
- PostgreSQL 13 (uses md5 by default, more compatible)
- Backend service with Docker network connectivity
- API service with Docker network connectivity
- Environment variables for Docker network hostname (`db`)

**`backend/Dockerfile`**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app:/data
CMD ["python", "-m", "alembic", "upgrade", "head"]
```

### Current Database Status

- **PostgreSQL Version:** 13
- **User:** paimana
- **Password:** paimanapass
- **Database:** paimana_ai
- **Tables Created:** 14 (including projects, playbooks, positive_deviants, etc.)

### API Endpoints Tested

- `GET /health` - Returns `{"status":"ok","service":"PAIMANA-AI"}`
- `GET /api/v1/playbooks` - Returns empty list (expected, no data yet)
- `GET /api/v1/positive-deviants` - Returns empty list (expected, no data yet)
- `GET /api/v1/projects` - Returns empty list (synthetic data module not available in container)

### For Development

When running the backend locally (not in Docker), you may still encounter authentication issues. For local development, consider:
1. Using Docker Compose for all services
2. Or configuring PostgreSQL to use `trust` authentication for localhost (development only)
3. Or using a local PostgreSQL installation instead of Docker

### Migration Status

Alembic migrations have been successfully run:
- `0001_core_tables` - Core section 6.2 tables
- `0002_positive_deviance_radar` - Positive Deviance Radar tables

### Summary

The PostgreSQL connectivity issue on Windows has been resolved by:
1. Using Docker network connectivity instead of localhost connections
2. Running all database operations (migrations, API) within Docker containers
3. Using PostgreSQL 13 for better compatibility with psycopg2-binary
4. Creating a Dockerfile for the backend to enable containerized builds
5. Adding API service to docker-compose for running the FastAPI server

The database is now accessible and the API is running successfully.
