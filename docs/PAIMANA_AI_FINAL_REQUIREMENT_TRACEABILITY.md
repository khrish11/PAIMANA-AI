# PAIMANA-AI Requirement Traceability Matrix (V2 Final)
*(SIH 2026 Demo Readiness)*

| SIH Requirement | PAIMANA Feature | Implementation Location | Evidence | Status | Limitations | Demo Readiness |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ingest Project Data** | CUF Submissions API & Bulk Import | `backend/app/api/v1/submissions.py`, `imports.py` | API endpoints and DB persistence verified. | ✅ IMPLEMENTED | None. | High |
| **Data Quality Assessment** | Data Confidence Score (DCS) | `backend/app/services/data_confidence.py` | Returns 0-100 score based on completeness, freshness, consistency, reliability. | ✅ IMPLEMENTED | Relies on default reliability if agency history missing. | High |
| **Predictive Risk Modeling** | XGBoost/LightGBM ML Models | `ml_pipeline/training/`, `production_ml_inference.py` | XGBoost/LightGBM experimental pipelines verified; SHAP implemented. | 🧪 EXPERIMENTAL | Trained on 160 projects; class imbalance handling (scale_pos_weight). | Medium (Advisory) |
| **Explainable AI (XAI)** | SHAP Explanations | `ml_pipeline/training/train_experimental_models.py` | `shap.TreeExplainer` actively extracts top 5 features. | ✅ IMPLEMENTED | Only explains ML components, not RCF/PBE. | High |
| **Historical Benchmarking** | Reference Class Forecasting (RCF) | `backend/app/services/rcf_engine.py` | Quantiles (P50, P80, P90) computed via SQL on completed projects. | ✅ IMPLEMENTED | Fallback to national average if <15 projects in cohort. | High |
| **Peer Comparison** | Peer-Pressure Benchmarking (PBE) | `backend/app/services/pbe_service.py` | Stage-aware cohorts, PPI score (0-100), percentiles, anonymization. | ✅ IMPLEMENTED | Limited by "Unknown" sector data in raw import. | High |
| **Automated Alerts** | Early Warning / Alerts API | `backend/app/api/v1/alerts.py` & `scheduler.py` | Alert generation integrated with data refresh. | ✅ IMPLEMENTED | - | High |
| **Actionable Escalation** | Governance Queue | `backend/app/api/v1/governance.py` | PostgreSQL persistence for governance actions/audit trails. | ✅ IMPLEMENTED | Simulated authority (no real approval/reject power yet). | High |
| **Text/Narrative Analysis** | Narrative Intelligence Detection (NID) | `backend/app/api/v1/nid.py` | Stubs exist; UI shows "unavailable". | 🔴 BLOCKED | Source PDF flash reports contain 0% narrative text. | Low (Disclosed Limitation) |
| **Positive Deviance** | Playbook Extractor | `backend/app/api/v1/positive_deviance.py` | Tests (`test_positive_deviance.py`) indicate 21 failures in this subsystem. | 🔴 BLOCKED | Implementation incomplete; tests failing. | Low |
| **Security & Auditing** | JWT RBAC & Audit Log Table | `backend/app/models/audit_log.py` | DB table exists; captures before/after states. | ✅ IMPLEMENTED | - | High |
