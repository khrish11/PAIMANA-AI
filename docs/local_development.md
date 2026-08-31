# Local Development Setup

This document describes how to set up PAIMANA-AI for local development.

## Prerequisites

- Python 3.13
- Node.js 18+
- Docker Desktop (for PostgreSQL and infrastructure)

## Quick Start (Docker - Recommended)

### 1. Start Infrastructure

```powershell
docker compose -f infra/docker-compose.yml up -d db
```

### 2. Verify Database

```powershell
python scripts/check_database.py
```

### 3. Run Migrations

```powershell
cd backend
alembic upgrade head
```

### 4. Start Backend

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

### 5. Start Frontend

```powershell
cd frontend
npm run dev
```

## Detailed Setup

### Backend Setup

```powershell
cd backend
pip install -r requirements.txt
```

### Frontend Setup

```powershell
cd frontend
npm install
```

### Database Setup

See [Docker Setup for Windows](docker_setup_windows.md) for detailed PostgreSQL setup.

## Running Tests

### Database-Independent Tests

```powershell
cd backend
python -m pytest backend/tests -q
```

### Database-Dependent Tests

```powershell
cd backend
python -m pytest backend/tests -m db -q
```

### Frontend Tests

```powershell
cd frontend
npm test
npm run lint
```

## Project Structure

```
SIH PROJECT/
├── backend/          # FastAPI application
├── frontend/         # React application
├── infra/            # Docker Compose configuration
├── data/             # Data files (separated by type)
├── docs/             # Documentation
├── ml_pipeline/      # ML training pipeline
├── scripts/          # Utility scripts
└── tests/            # Test files
```

## Data Organization

- **Real PAIMANA Data:** `data/REPORTS 25/`, `data/REPORTS 26/`, `data/extracted/`, `data/processed/`
- **Synthetic Data:** `data/synthetic/` (testing only)
- **Training Data:** `data/training/`
- **Validation Data:** `data/validation/`

## Development Workflow

1. Make code changes
2. Run database-independent tests
3. Start Docker services (if needed)
4. Run database-dependent tests
5. Verify with frontend
6. Build and lint before committing

## Troubleshooting

### Docker Issues

See [Docker Setup for Windows](docker_setup_windows.md)

### Database Connection

Run `python scripts/check_database.py` to diagnose connection issues.

### Python Dependencies

```powershell
cd backend
pip install --upgrade -r requirements.txt
```

### Node Dependencies

```powershell
cd frontend
npm install
```

## Environment Variables

Copy `.env.example` to `.env` and configure as needed:

```powershell
cp .env.example .env
```

## Performance Notes

- Large data directories are excluded from watchers
- Tests ignore large data folders
- Build process excludes data directories

## Architecture

- **Backend:** FastAPI + PostgreSQL 16
- **Frontend:** React + Vite
- **Infrastructure:** Docker Compose
- **ML:** scikit-learn, XGBoost, LightGBM
- **LLM:** Ollama (via Docker)
