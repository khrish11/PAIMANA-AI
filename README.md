# PAIMANA-AI

AI-powered predictive analytics and early-warning system for infrastructure project monitoring, built for Smart India Hackathon 2026.

This repository follows the SRS Section 14.1 layout exactly:

- `backend/`: FastAPI application for API, processing, and online inference services.
- `ml_pipeline/`: offline ETL, model training, evaluation, and model artifact staging.
- `frontend/`: React 18 presentation layer.
- `infra/`: Docker Compose, container images, Nginx, and monitoring configuration.
- `data/`: synthetic seed data and schema dictionaries only. Real PAIMANA/CUF data must not be committed.
- `docs/`: SRS-derived notes, model cards, diagrams, and ADRs.
- `scripts/`: operational scripts such as refresh, seeding, and backfills.

Current implementation scope: Phase 0 and Phase 1 only. Later features are represented by placeholders where the SRS requires their files to live.

## Project Status & Validation Summary

### Data Pipeline Validation (Completed August 2026)

**Database Health:**
- 2,634 projects imported from PAIMANA Flash Report data
- 19,793 CUF submissions (13 reporting months: July 2025 - July 2026)
- Total sanctioned cost: ₹7,084,743 Cr
- Average physical progress: 57.3%

**Data Quality Metrics:**
- Sector: 83.1% Unknown (source data limitation - sector not in project-level tables)
- Ministry: ~65% mapped via agency-to-ministry mapping (improved from 23%)
- State: 99.6% coverage (11 projects have state in name but not extracted)
- Agency: 93.5% coverage (6.5% missing - source limitation)
- Narrative: 0% coverage (source PDFs lack narrative text field)
- Status: 100% Active (source lacks status field, default applied)

**Intelligence Components - Real Data Verification:**

✅ **Reference Class Forecasting (RCF)**
- Uses PostgreSQL database for completed projects
- Fallback to synthetic data only when reference class < 15 samples
- Completion criteria: status (completed/closed/finished), physical_progress >= 100%, or expenditure >= sanctioned_cost
- No synthetic data used in production RCF path

✅ **Peer-Pressure Benchmarking Engine (PBE)**
- Uses real database data for peer filtering
- Filters by sector, size band, and state
- Self-exclusion implemented at service level
- Handles low-data scenarios (0, 1, 5, 9, 10 peers)

✅ **Data Confidence Score (DCS)**
- Thresholds verified: LOW (0-49.99), MODERATE (50-79.99), HIGH (80-100)
- Correlation with risk scores: 0.015 (very weak, properly separated)
- Components: completeness, freshness, consistency, reliability

✅ **Risk Scoring**
- Weights confirmed: Cost 30%, Schedule 25%, Progress 25%, Governance 20%
- Component distribution: Governance 100% zero, Cost/Schedule 75% zero, Progress 69.6% zero
- Risk category distribution: LOW 82.8%, MODERATE 5.3%, HIGH 5.8%, VERY_HIGH 6.2%

⚠️ **Known Synthetic Data Dependencies:**
- Network Intelligence: Uses `synthetic_data.load_projects()` (not database)
- Positive Deviance Radar: Uses `synthetic_data.get_completed_projects_df()` (not database)
- Governance Queue: In-memory storage only (not PostgreSQL)
- Audit API: In-memory storage only (not PostgreSQL)

**Test Results:**
- Backend Tests: 62 passed, 21 failed (PDR/simulation API tests - not data pipeline related)
- DB Tests: PostgreSQL connection successful via Docker internal network
- Frontend Tests: Failed (React import issues in test files)
- Frontend Lint: Passed
- Frontend Build: Passed

### Current Existing Problems

**Data Quality Issues (Source Limitations):**
1. **Sector Coverage (83.1% Unknown)**: Source PAIMANA PDFs do not contain sector information in project-level tables. Sector is only available in summary tables, making direct mapping difficult.
2. **Narrative Data (0% Coverage)**: Source PDFs lack narrative text fields entirely. NID (Narrative Intelligence Detector) cannot function without this data.
3. **Project Status (100% Active Default)**: Source lacks a status field. All projects default to "Active" status, which affects RCF completion detection.
4. **Risk Component Sparsity**: 
   - Governance Risk: 100% zero values (no governance data in source)
   - Cost/Schedule Risk: 75% zero values (insufficient historical data)
   - Progress Anomaly: 69.6% zero values

**Synthetic Data Dependencies:**
1. **Network Intelligence**: Currently uses `synthetic_data.load_projects()` instead of database queries. Needs migration to real data.
2. **Positive Deviance Radar**: Uses `synthetic_data.get_completed_projects_df()` instead of database queries.
3. **Governance Queue**: Uses in-memory storage instead of PostgreSQL persistence.
4. **Audit Trail**: Uses in-memory storage instead of PostgreSQL persistence.

**Test Failures:**
1. **Frontend Tests**: 35 tests failed due to React import issues in test files (missing `import React` statements).
2. **Backend PDR/Simulation Tests**: 21 tests failed due to authentication issues (401 Unauthorized) and missing dependencies.

**Frontend Issues:**
1. Test files missing React imports
2. Some components may not be fully integrated with real API endpoints

## System Architecture

### Backend Design

**Technology Stack:**
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16 with SQLAlchemy ORM
- **Authentication**: JWT-based (currently has test failures)
- **API Documentation**: OpenAPI/Swagger auto-generated

**Directory Structure:**
```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   └── v1/          # API version 1
│   │       ├── projects.py      # Project CRUD, RCF, PBE endpoints
│   │       ├── risk.py          # Risk scoring endpoints
│   │       ├── governance.py    # Governance queue endpoints
│   │       ├── audit.py         # Audit trail endpoints (in-memory)
│   │       ├── network.py       # Network intelligence endpoints
│   │       └── positive_deviance.py  # PDR endpoints
│   ├── core/             # Configuration, security
│   │   └── config.py     # Settings from environment variables
│   ├── db/               # Database session management
│   │   └── session.py    # SQLAlchemy session factory
│   ├── models/           # SQLAlchemy ORM models
│   │   ├── projects.py           # Project table
│   │   ├── cuf_submissions.py    # Monthly submissions
│   │   ├── risk_scores.py        # Risk score records
│   │   └── governance_actions.py  # Governance actions
│   └── services/         # Business logic
│       ├── rcf_engine.py         # Reference Class Forecasting
│       ├── pbe_service.py        # Peer-Pressure Benchmarking
│       ├── risk_scoring.py       # Risk calculation
│       ├── data_confidence.py    # DCS calculation
│       ├── governance_service.py # Governance escalation
│       ├── network_intelligence.py  # Dependency graphs (synthetic)
│       └── positive_deviance.py  # PDR (synthetic)
├── tests/                # Test suite
└── import_paimana_data.py # Data import script
```

**Key Services:**

1. **RCF Engine (`rcf_engine.py`)**
   - Queries PostgreSQL for completed projects
   - Groups by sector, state, size band
   - Calculates cost overrun statistics
   - Fallback to synthetic data if < 15 samples

2. **PBE Service (`pbe_service.py`)**
   - Filters peers by sector, size band, state
   - Self-excludes target project
   - Calculates percentile benchmarks
   - Handles low-data scenarios gracefully

3. **Risk Scoring (`risk_scoring.py`)**
   - Composite score: Cost (30%) + Schedule (25%) + Progress (25%) + Governance (20%)
   - Categories: LOW, MODERATE, HIGH, VERY_HIGH, CRITICAL
   - Thresholds: low_max=30, moderate_max=50, high_max=70, very_high_max=85

4. **Data Confidence (`data_confidence.py`)**
   - Components: completeness, freshness, consistency, reliability
   - Labels: LOW (0-49.99), MODERATE (50-79.99), HIGH (80-100)
   - Independent from risk scoring (correlation 0.015)

**API Endpoints:**
- `GET /api/v1/projects` - List projects with pagination
- `GET /api/v1/projects/{id}` - Get project details
- `GET /api/v1/projects/{id}/rcf` - Get RCF forecast
- `GET /api/v1/projects/{id}/pbe` - Get PBE benchmark
- `GET /api/v1/projects/{id}/risk` - Get risk score
- `GET /api/v1/projects/{id}/network` - Get network intelligence
- `GET /api/v1/governance/queue` - Get governance queue
- `GET /api/v1/audit` - Get audit trail

### Database Design

**PostgreSQL Schema:**

**1. Projects Table**
```sql
CREATE TABLE projects (
    project_id UUID PRIMARY KEY,
    project_name VARCHAR(255),
    sector VARCHAR(120),           -- 83.1% Unknown
    ministry VARCHAR(160),         -- ~65% mapped
    state VARCHAR(120),           -- 99.6% coverage
    agency VARCHAR(255),
    project_code VARCHAR(100),
    sanctioned_cost NUMERIC(15,2),
    approved_date DATE,
    status VARCHAR(50),           -- 100% Active (default)
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**2. CUF Submissions Table**
```sql
CREATE TABLE cuf_submissions (
    submission_id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(project_id),
    reporting_month DATE,          -- 2025-07 to 2026-07
    revised_cost NUMERIC(15,2),
    expenditure NUMERIC(15,2),
    physical_progress NUMERIC(5,2),
    planned_completion DATE,
    narrative_text TEXT,           -- 0% populated
    submitted_by VARCHAR(160),
    submitted_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(project_id, reporting_month)
);
```

**3. Risk Scores Table**
```sql
CREATE TABLE risk_scores (
    score_id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(project_id),
    reporting_month DATE,
    composite_score NUMERIC(5,2),
    risk_category VARCHAR(20),     -- LOW, MODERATE, HIGH, VERY_HIGH, CRITICAL
    cost_risk NUMERIC(5,2),           -- 75% zero
    schedule_risk NUMERIC(5,2),       -- 75% zero
    progress_anomaly_score NUMERIC(5,2), -- 69.6% zero
    governance_risk NUMERIC(5,2),      -- 100% zero
    data_confidence_score NUMERIC(5,2),
    created_at TIMESTAMP,
    UNIQUE(project_id, reporting_month)
);
```

**4. Governance Actions Table**
```sql
CREATE TABLE governance_actions (
    action_id VARCHAR(32) PRIMARY KEY,
    project_id UUID REFERENCES projects(project_id),
    action_type VARCHAR(80),
    triggered_by VARCHAR(160),
    reviewed_by VARCHAR(160),
    outcome TEXT,
    timestamp TIMESTAMP,
    INDEX(project_id)
);
-- Note: Currently 0 records (in-memory storage used)
```

**Data Import Process:**
1. PAIMANA PDFs → CSV extraction (`data/extracted/`)
2. CSV normalization (`data/processed/all_projects_normalized.csv`)
3. Agency/ministry/sector mapping (`data/validation/agency_ministry_sector_mapping.json`)
4. PostgreSQL import via `import_paimana_data.py`
5. Idempotent: detects existing records, updates only if changed

**Database Statistics:**
- Total Projects: 2,634
- Total Submissions: 19,793
- Avg Submissions/Project: 7.5
- Reporting Period: 13 months (July 2025 - July 2026)
- Total Sanctioned Cost: ₹7,084,743 Cr

### Frontend Design

**Technology Stack:**
- **Framework**: React 18.3.1
- **Build Tool**: Vite
- **State Management**: Zustand
- **Data Fetching**: @tanstack/react-query
- **Routing**: React Router DOM 7.18.3
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Testing**: Vitest, @testing-library/react

**Directory Structure:**
```
frontend/
├── src/
│   ├── components/       # Reusable components
│   │   ├── common/      # Shared UI components
│   │   ├── projects/    # Project-related components
│   │   ├── risk/        # Risk visualization components
│   │   ├── governance/  # Governance queue components
│   │   └── playbooks/   # Playbook library components
│   ├── pages/           # Page-level components
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API service layer
│   ├── store/           # Zustand state management
│   └── utils/           # Utility functions
├── public/              # Static assets
└── package.json
```

**Key Components:**

1. **Project Dashboard**
   - Project list with filtering and search
   - Project detail view
   - Risk score visualization
   - RCF and PBE results display

2. **Risk Visualization**
   - Risk score gauges
   - Component breakdown charts
   - Risk category indicators
   - Historical trend charts

3. **Governance Queue**
   - HIGH+ risk project listing
   - Escalation criteria display
   - Action tracking interface

4. **Playbook Library**
   - Positive deviance playbooks
   - Filtering by category and confidence
   - Playbook detail views

**State Management:**
- Zustand stores for:
  - Project list state
  - Risk score state
  - User preferences
  - Filter settings

**API Integration:**
- React Query for data fetching and caching
- Axios for HTTP requests
- Error boundary for error handling
- Loading states for async operations

**Current Issues:**
- Test files missing React imports (35 tests failing)
- Some components may need integration with real API endpoints
- Build succeeds, but tests need fixing

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop (for PostgreSQL)

### Setup

1. **Start PostgreSQL (Docker)**
   ```powershell
   docker compose -f infra/docker-compose.yml up -d db
   ```

2. **Verify Database**
   ```powershell
   python scripts/check_database.py
   ```

3. **Run Migrations**
   ```powershell
   cd backend
   alembic upgrade head
   ```

4. **Import PAIMANA Data**
   ```powershell
   python import_paimana_data.py
   ```

5. **Start Backend**
   ```powershell
   python -m uvicorn app.main:app --reload --port 8001
   ```

6. **Start Frontend**
   ```powershell
   cd frontend
   npm run dev
   ```

### Docker Quick Start

To run all services with Docker:
```powershell
docker compose -f infra/docker-compose.yml up -d
```

Access the application at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## Documentation

- [Local Development Setup](docs/local_development.md) - Complete development guide
- [Docker Setup for Windows](docs/docker_setup_windows.md) - Docker-specific setup
- [Positive Deviance Radar](docs/positive_deviance_radar.md) - PDR feature documentation

## Testing

### Database-Independent Tests
```powershell
cd backend
python -m pytest backend/tests -q --ignore=tests/test_chronological_split.py --ignore=tests/test_feature_engineering.py
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
npm run build
```

## Architecture Summary

- **Backend:** FastAPI + PostgreSQL 16 + SQLAlchemy ORM
- **Frontend:** React 18 + Vite + Zustand + React Query
- **Infrastructure:** Docker Compose
- **ML:** scikit-learn, XGBoost, LightGBM
- **LLM:** Ollama (via Docker)

## Data Pipeline

1. **Source**: PAIMANA Flash Report PDFs
2. **Extraction**: Tabula-py for table extraction
3. **Normalization**: CSV consolidation and cleaning
4. **Mapping**: Agency-to-ministry/sector mapping
5. **Import**: PostgreSQL via SQLAlchemy
6. **Intelligence**: RCF, PBE, DCS, Risk Scoring

## Known Limitations

1. **Sector Data**: 83.1% Unknown due to source structure
2. **Narrative Data**: 0% coverage - source lacks narrative fields
3. **Network Intelligence**: Uses synthetic data (needs migration)
4. **PDR**: Uses synthetic data (needs migration)
5. **Governance/Audit**: In-memory storage (needs PostgreSQL persistence)

## Future Work

1. Migrate Network Intelligence to real database queries
2. Migrate PDR to real database queries
3. Implement PostgreSQL persistence for governance queue
4. Implement PostgreSQL persistence for audit trail
5. Fix frontend test React import issues
6. Improve sector mapping from summary tables
7. Add project status field to import process
8. Enhance risk component calculations with historical data
