# PAIMANA-AI Risk Register (V2 Final)
*(Technical Limitations and Operational Risks)*

## 1. Data Quality and Limitations

### 1.1 Unknown Sector Data
- **Evidence**: Data analysis indicates 83.1% of imported projects have an "Unknown" sector.
- **Impact**: Limits the effectiveness of Reference Class Forecasting (RCF) and Peer-Pressure Benchmarking (PBE), which rely on sector categorization to form accurate cohorts.
- **Severity**: HIGH
- **Mitigation**: PBE and RCF logic gracefully degrade (e.g., RCF falls back to national averages when cluster size < 15). Data hygiene practices must improve upstream.

### 1.2 Missing Narrative Data
- **Evidence**: Source PDF flash reports lack narrative text fields (0% coverage).
- **Impact**: NLP/LLM features like Narrative Intelligence Detection (NID) and Positive Deviance Recommender (PDR) are completely blocked. The UI displays these as "unavailable."
- **Severity**: MEDIUM (Expected for Phase 1, but blocks Phase 2/3 features).
- **Mitigation**: Future ingestion pipelines must scrape textual status notes.

### 1.3 Missing Status Fields
- **Evidence**: 100% of projects are defaulted to "Active".
- **Impact**: Prevents automatic detection of completed or stalled projects via the status field, requiring reliance on physical progress (>= 100%) or expenditure thresholds.
- **Severity**: MEDIUM
- **Mitigation**: Backend heuristically assigns completion if physical progress is >= 100%.

## 2. Machine Learning Risks

### 2.1 Extremely Small Training Dataset
- **Evidence**: XGBoost and Random Forest models were trained on exactly 160 labeled completed projects (as verified in `ml_pipeline/training/train_experimental_models.py`).
- **Impact**: High risk of model overfitting and poor generalization to new projects.
- **Severity**: HIGH
- **Mitigation**: Models are treated as experimental/advisory only. Final composite risk heavily weights deterministic components (Cost, Schedule, Progress).

### 2.2 Class Imbalance
- **Evidence**: Schedule delay > 6 months is positive for 59.4% of the 160 projects.
- **Severity**: MEDIUM
- **Mitigation**: `scale_pos_weight` is correctly calculated and applied dynamically during XGBoost training.

## 3. Architecture and Operational Risks

### 3.1 Positive Deviance / Simulation API Failures
- **Evidence**: Current test run shows 21 failures out of 120 tests, specifically concentrated in `test_positive_deviance.py`, `test_positive_deviance_api.py`, and `test_simulation_api.py`.
- **Impact**: The Positive Deviance and Simulation sub-systems are currently broken and should not be demoed.
- **Severity**: MEDIUM (These are stretch features).
- **Mitigation**: Disable these endpoints for the SIH demo and focus on Core Risk, RCF, PBE, and Governance.

### 3.2 Synchronous Intelligence Refresh Bottleneck
- **Evidence**: `backend/app/api/v1/submissions.py` natively calls `refresh_project_intelligence` during the HTTP request cycle.
- **Impact**: Ingesting a CUF submission forces the user to wait for DB recalculations, RCF generation, and potentially ML inference.
- **Severity**: HIGH (Will timeout under scale).
- **Mitigation**: Future architecture should queue this task to a Celery/Redis worker.
