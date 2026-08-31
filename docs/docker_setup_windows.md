# Docker Setup for Windows

PAIMANA-AI requires Docker Desktop to run PostgreSQL and other infrastructure services on Windows.

## Prerequisites

1. **Docker Desktop for Windows**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install with WSL 2 backend (recommended)
   - Start Docker Desktop after installation

2. **Verify Docker Installation**
   ```powershell
   docker --version
   docker compose version
   docker ps
   ```

## Database Setup

### 1. Start PostgreSQL Service

From the project root:
```powershell
docker compose -f infra/docker-compose.yml up -d db
```

This starts PostgreSQL 16 with:
- User: `paimana`
- Password: `paimana_dev_password`
- Database: `paimana_ai`
- Port: `5432`

### 2. Verify Database Health

```powershell
docker compose -f infra/docker-compose.yml ps db
```

Wait for the healthcheck to pass (may take 10-30 seconds).

### 3. Run Database Check

```powershell
python scripts/check_database.py
```

Expected output:
```
DATABASE CONNECTION: OK
```

### 4. Run Database Migrations

```powershell
cd backend
alembic upgrade head
```

This applies all migrations including:
- `0001_core_tables`
- `0002_positive_deviance_radar`

## Backend Startup

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8001
```

Verify health endpoint:
```powershell
curl http://localhost:8001/health
```

## Frontend Startup

```powershell
cd frontend
npm run dev
```

Access at: http://localhost:5173

## Full Infrastructure

To start all services (PostgreSQL, Redis, MinIO, Ollama):
```powershell
docker compose -f infra/docker-compose.yml up -d
```

## Troubleshooting

### Docker Desktop Not Running

**Error:** `error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/v1.49/containers/json"`

**Solution:** Start Docker Desktop from Windows Start menu

### Port Already in Use

**Error:** `port 5432 is already allocated`

**Solution:** Stop other PostgreSQL instances or change port in `docker-compose.yml`

### Database Connection Failed

**Error:** `FATAL: password authentication failed for user "paimana"`

**Solution:** Ensure credentials match between `.env.example` and running container

## Development Workflow

1. Start Docker Desktop
2. Start PostgreSQL: `docker compose -f infra/docker-compose.yml up -d db`
3. Check database: `python scripts/check_database.py`
4. Run migrations: `cd backend && alembic upgrade head`
5. Start backend: `python -m uvicorn app.main:app --reload --port 8001`
6. Start frontend: `cd frontend && npm run dev`

## Stopping Services

```powershell
docker compose -f infra/docker-compose.yml down
```

To preserve database data:
```powershell
docker compose -f infra/docker-compose.yml down -v
```

## Architecture Notes

- **Production database:** PostgreSQL 16 (no SQLite fallback)
- **Development database:** PostgreSQL 16 via Docker
- **No local PostgreSQL installation required** when using Docker
- **Database schema:** Defined in Alembic migrations
- **Data persistence:** Docker volume `postgres_data`

## Security Notes

- Development credentials are in `.env.example` (do not commit real secrets)
- Production credentials should use environment variables
- Never commit `.env` file with real passwords
