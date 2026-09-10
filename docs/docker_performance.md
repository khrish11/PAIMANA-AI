# Docker Performance Optimization Report

## Root Cause Analysis

### Critical Issues Identified

1. **Entire Repository Mounted in API Container**
   - **Location**: `infra/docker-compose.yml` line 53
   - **Issue**: `api` service had volume mount `- ../:/project_root`
   - **Impact**: Mounted entire repository including:
     - `data/extracted/` (~3,243 CSV files)
     - `data/REPORTS 25/`, `data/REPORTS 26/` (PDFs)
     - `data/training/` (large ML artifacts)
     - `frontend/node_modules/`
     - All other data directories
   - **Platform Impact**: Windows + WSL2 + Docker Desktop has known performance issues with large bind mounts

2. **Frontend Build Context Too Large**
   - **Location**: `infra/docker-compose.yml` line 84
   - **Issue**: `frontend` build context was `context: ..` (entire repo)
   - **Impact**: Docker scanned entire repository during frontend builds

3. **Missing .dockerignore Files**
   - **Issue**: No `.dockerignore` files existed in:
     - Root directory
     - `backend/`
     - `frontend/`
   - **Impact**: Docker copied/scanned all files during builds, including:
     - Data directories
     - Node modules
     - Python cache
     - Git history
     - Documentation

4. **Dockerfile Layer Issues**
   - **Frontend Dockerfile**: Used `WORKDIR /app/frontend` and copied from `frontend/` prefix
   - **Impact**: Unnecessary path complexity and potential context issues

## Changes Made

### 1. Created `.dockerignore` Files

#### Root `.dockerignore`
```
# Data directories - these contain thousands of files
data/extracted/
data/REPORTS 25/
data/REPORTS 26/
data/training/
data/processed/
data/validation/
data/artifacts/
data/

# Frontend dependencies
frontend/node_modules/
frontend/dist/
frontend/.vite/

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so

# Build artifacts
build/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Documentation
docs/
*.md
!README.md

# Logs
*.log

# Environment
.env
.env.local

# Docker
.dockerignore
Dockerfile
docker-compose.yml
infra/

# Scripts
*.sh
get_baseline*.py
test_*.py

# Temporary files
*.tmp
*.bak
```

#### Backend `.dockerignore`
```
# Data directories
data/
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Git
.git/
.gitignore

# Documentation
docs/
*.md
!README.md

# Logs
*.log

# Environment
.env
.env.local
```

#### Frontend `.dockerignore`
```
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

# Build output
dist/
dist-ssr/
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment
.env
.env.local
.env.production.local
.env.development.local
.env.test.local
```

### 2. Optimized `docker-compose.yml`

#### API Service (Lines 34-54)
**Before:**
```yaml
volumes:
  - ../backend:/app
  - ../:/project_root  # ← ENTIRE REPOSITORY MOUNTED
environment:
  PYTHONPATH: /app:/project_root
```

**After:**
```yaml
volumes:
  - ../backend:/app  # ← ONLY BACKEND MOUNTED
environment:
  PYTHONPATH: /app
```

#### Frontend Service (Lines 80-89)
**Before:**
```yaml
build:
  context: ..  # ← ENTIRE REPOSITORY AS BUILD CONTEXT
  dockerfile: infra/Dockerfile.frontend
```

**After:**
```yaml
build:
  context: ../frontend  # ← ONLY FRONTEND AS BUILD CONTEXT
  dockerfile: ../infra/Dockerfile.frontend
```

### 3. Optimized Frontend Dockerfile

**Before:**
```dockerfile
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend ./
```

**After:**
```dockerfile
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
```

## Expected Performance Improvements

### Build Context Size
- **Before**: Entire repository (~GBs with data files)
- **After**: 
  - Backend build: Only `backend/` directory
  - Frontend build: Only `frontend/` directory
- **Estimated reduction**: 90%+ context size reduction

### Bind Mount Overhead
- **Before**: Entire repository mounted in API container
- **After**: Only `backend/` mounted
- **Impact**: Eliminated Windows filesystem overhead for data directories

### Docker Layer Caching
- **Backend**: Dependencies installed before code copy (already optimized)
- **Frontend**: Dependencies installed before source copy (already optimized)
- **Impact**: Dependency layers cached unless `requirements.txt` or `package.json` changes

## Database Safety

### Baseline Counts (To Be Verified)
- Projects: ~2,636
- CUF Submissions: ~19,798

### Data Preservation
- **No changes to**: PostgreSQL volume, data directories, model artifacts
- **Only changed**: Docker configuration files
- **Risk**: None - data files remain untouched

## Development Workflow

### Commands to Use

**Start services:**
```bash
cd infra
docker-compose up -d db api
```

**Restart only API:**
```bash
docker-compose restart api
```

**Rebuild only API:**
```bash
docker-compose build api
docker-compose up -d api
```

**Check status:**
```bash
docker-compose ps
```

**Database query:**
```bash
docker-compose exec db psql -U paimana -d paimana_ai -c "SELECT COUNT(*) FROM projects"
```

### Commands to Avoid

**Do NOT use:**
```bash
docker-compose down -v  # ← Destroys PostgreSQL volume
docker-compose build --no-cache  # ← Ignores all caching
docker-compose up --build  # ← Rebuilds everything
```

**Do NOT mount:**
- Entire repository
- Data directories
- Node modules
- Python cache

## Platform-Specific Notes

### Windows + WSL2 + Docker Desktop
- **Issue**: Bind mount performance degrades with many files
- **Solution**: Minimize bind mount scope
- **Avoid**: Mounting large static data directories

### File Watchers
- Vite should ignore: `data/**`, `node_modules/**`, `dist/**`
- Python should ignore: `__pycache__/**`, `*.pyc`

## Verification Steps

1. **Test Docker commands speed:**
   ```bash
   docker-compose ps  # Should complete in seconds
   docker-compose exec db psql -U paimana -d paimana_ai -c "SELECT 1"  # Should complete in seconds
   ```

2. **Test build speed:**
   ```bash
   docker-compose build api  # Should complete in minutes, not 15-30 minutes
   ```

3. **Verify database intact:**
   ```bash
   docker-compose exec db psql -U paimana -d paimana_ai -c "SELECT COUNT(*) FROM projects"
   ```

4. **Verify API functionality:**
   ```bash
   curl http://localhost:8001/api/v1/health
   ```

## Next Steps

After performance is verified:
1. Resume continuous operations E2E test
2. Verify LightGBM loads without libgomp errors
3. Run full DB tests
4. Run frontend tests
5. Document all fixes in acceptance report

## Summary

**Root Cause**: Entire repository mounted and scanned by Docker, causing severe performance degradation on Windows + WSL2.

**Solution**: 
- Created `.dockerignore` files to exclude data directories
- Removed unnecessary repository-wide bind mount
- Changed frontend build context to only `frontend/`
- Optimized Dockerfile paths

**Expected Result**: 
- Build context reduced by 90%+
- Docker commands complete in seconds instead of minutes
- No impact on data or functionality
