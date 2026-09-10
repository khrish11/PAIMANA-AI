# PAIMANA-AI Requirement Traceability Matrix
*(SIH 2026 Demo Readiness)*

| SIH Requirement | PAIMANA Feature | Implementation Location | Evidence | Status | Limitations | Demo Readiness |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Ingest Project Data** | CUF Submissions API & Bulk Import | `backend/app/api/v1/submissions.py`, `imports.py` | API endpoints and DB persistence verified. | ✅ IMPLEMENTED | None. | High |
| **Data Quality Assessment** | Data Confidence Score (DCS) | `backend/app/services/data_confidence.py` | Returns 0-100 score based on completeness, freshness, consistency, reliability. | ✅ IMPLEMENTED | Relies on default reliability if agency history missing. | High |
| **Predictive Risk Modeling** | XGBoost/LightGBM ML Models | `ml_pipeline/training/` & `risk_scoring.py` | Models stored in MinIO; `ml_cost_risk` fields exist in DB. | 🧪 EXPERIMENTAL | Trained on only 160 completed projects. | Medium (Advisory) |
| **Explainable AI (XAI)** | SHAP Explanations | `backend/app/models/risk_scores.py` | `shap_drivers` JSONB field in RiskScore table. | ✅ IMPLEMENTED | Only explains ML components, not RCF/PBE. | High |
| **Historical Benchmarking** | Reference Class Forecasting (RCF) | `backend/app/services/rcf_engine.py` | Quantiles (P50, P80, P90) computed from PostgreSQL completed projects. | ✅ IMPLEMENTED | Fallback to national average if <15 projects in cohort. | High |
| **Peer Comparison** | Peer-Pressure Benchmarking (PBE) | `backend/app/services/pbe_service.py` | Stage-aware cohorts, PPI score, percentiles. | ✅ IMPLEMENTED | Limited by 83.1% "Unknown" sector data in raw import. | High |
| **Automated Alerts** | Early Warning / Alerts API | `backend/app/api/v1/alerts.py` & `scheduler.py` | Alert generation integrated with data refresh. | ✅ IMPLEMENTED | - | High |
| **Actionable Escalation** | Governance Queue | `backend/app/api/v1/governance.py` | PostgreSQL persistence for governance actions/audit trails. | ✅ IMPLEMENTED | Simulated authority (no real approval/reject power yet). | High |
| **Text/Narrative Analysis** | Narrative Intelligence Detection (NID) | `backend/app/api/v1/nid.py` | Stubs exist; UI shows "unavailable". | 🔴 BLOCKED | Source PDF flash reports contain 0% narrative text. | Low (Disclosed Limitation) |
| **Security & Auditing** | JWT RBAC & Audit Log Table | `backend/app/models/audit_log.py` | DB table exists; captures before/after states. | 🟡 PARTIAL | JWT authentication has failing test coverage. | Medium |

*(Generated automatically from strict read-only codebase audit)*
