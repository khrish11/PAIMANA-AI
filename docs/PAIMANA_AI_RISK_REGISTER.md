# PAIMANA-AI Risk Register
*(Technical Limitations and Operational Risks)*

## 1. Data Quality and Limitations

### 1.1 Unknown Sector Data
- **Evidence**: `README.md` and data analysis scripts indicate 83.1% of imported projects have an "Unknown" sector.
- **Impact**: Limits the effectiveness of Reference Class Forecasting (RCF) and Peer-Pressure Benchmarking (PBE), which rely on sector categorization to form accurate cohorts.
- **Severity**: HIGH

### 1.2 Missing Narrative Data
- **Evidence**: Source PDF flash reports lack narrative text fields (0% coverage).
- **Impact**: NLP/LLM features like Narrative Intelligence Detection (NID) and Positive Deviance Recommender (PDR) are completely blocked. The UI displays these as "unavailable."
- **Severity**: MEDIUM (Expected for Phase 1, but blocks Phase 2/3 features).

### 1.3 Missing Status Fields
- **Evidence**: 100% of projects are defaulted to "Active".
- **Impact**: Prevents automatic detection of completed or stalled projects via the status field, requiring reliance on physical progress (>= 100%) or expenditure thresholds.
- **Severity**: MEDIUM

## 2. Machine Learning Risks

### 2.1 Extremely Small Training Dataset
- **Evidence**: XGBoost and Random Forest models were trained on only 160 completed projects.
- **Impact**: High risk of model overfitting and poor generalization to new projects. Predictions have high uncertainty and are strictly advisory.
- **Severity**: HIGH

### 2.2 Class Imbalance
- **Evidence**: Infrastructure projects historically skew towards cost overruns and schedule delays, meaning standard machine learning models may struggle to predict rare "on-time/on-budget" outcomes without proper SMOTE/balancing techniques.
- **Severity**: MEDIUM

## 3. Architecture and Security Risks

### 3.1 Failing Authentication Tests
- **Evidence**: `README.md` notes that JWT authentication tests are failing.
- **Impact**: If deployed as-is, API endpoints may be vulnerable to unauthorized access or privilege escalation.
- **Severity**: CRITICAL (Must be resolved before production).

### 3.2 Simulated Governance Authority
- **Evidence**: `backend/app/api/v1/governance.py` allows state transitions, but there is no actual integration with a real identity provider or government approval authority.
- **Impact**: The workflow is a prototype simulation; it is not yet suitable for legally binding governance actions.
- **Severity**: LOW (Acceptable for Demo/Hackathon).

## 4. Performance and Operational Risks

### 4.1 Sync vs Async Bottlenecks
- **Evidence**: `backend/app/api/v1/submissions.py` natively calls `refresh_project_intelligence` during the HTTP request cycle.
- **Impact**: Ingesting a CUF submission forces the user to wait for DB recalculations, RCF generation, and potentially ML inference. This could cause timeouts under heavy load.
- **Severity**: HIGH (Recommend moving intelligence refresh to a background worker via Celery/APScheduler).
