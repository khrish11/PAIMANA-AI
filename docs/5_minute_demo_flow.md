# 5-Minute SIH Judge Demo Flow

**Date:** August 31, 2026  
**Purpose:** Deterministic 5-minute demonstration flow for SIH 2026 judges  
**Target Audience:** SIH 2026 Judges  
**Total Duration:** 5 minutes

---

## DEMO OVERVIEW

This demo flow is designed to showcase the PAIMANA AI system's key capabilities within a strict 5-minute timeframe. The flow is deterministic, uses real PAIMANA data, and explicitly discloses all limitations at appropriate points.

**Key Principles:**
- Use real PAIMANA data only
- Explicitly disclose all limitations
- Keep each section to 30-45 seconds
- Focus on high-impact features
- End with clear next steps

---

## TIMELINE

### 00:00 - 00:20 (20 seconds): Login & Dashboard

**Screen:** Login → National Dashboard

**What Judge Sees:**
- Login screen with role selection (ADMIN)
- National Dashboard with real PAIMANA metrics
- Total Projects: 2,634
- Risk distribution charts
- State-wise project distribution

**What to Say:**
> "Welcome to PAIMANA AI. I'm logging in as an administrator. This is the National Dashboard showing real PAIMANA data from 2,634 infrastructure projects across India. You can see the risk distribution - most projects are LOW or MODERATE risk, with 336 projects requiring governance review."

**Data Source:** Real PAIMANA database (PostgreSQL)

**Limitation to Disclose:** None for this section

---

### 00:20 - 01:00 (40 seconds): Select HIGH/VERY_HIGH Project

**Screen:** National Dashboard → Project List → Project Detail

**What Judge Sees:**
- Project list filtered by HIGH/VERY_HIGH risk
- Click on a VERY_HIGH risk project (e.g., Project 6e2b1806)
- Project Detail page loads

**What to Say:**
> "Let me select a high-risk project to demonstrate the intelligence features. I'm filtering for VERY_HIGH risk projects and selecting this Telangana project with a risk score of 72.5. This project shows sudden cost escalation from ₹1,402 Cr to ₹2,509 Cr - a 79% increase."

**Data Source:** Real PAIMANA database (PostgreSQL)

**Limitation to Disclose:** None for this section

---

### 01:00 - 01:20 (20 seconds): Project Summary & Risk Intelligence

**Screen:** Project Detail → Risk Intelligence Section

**What Judge Sees:**
- Project summary card
- Risk intelligence with composite score
- Risk category (VERY_HIGH)
- Risk components breakdown

**What to Say:**
> "This is the Project Detail page. The Risk Intelligence section shows a composite score of 72.5, categorized as VERY_HIGH. The risk components show cost risk at 100%, schedule risk at 100%, and progress anomaly at 70%. The Data Confidence Score is 78.5 with MODERATE confidence."

**Data Source:** Real PAIMANA database (PostgreSQL)

**Limitation to Disclose:** 
> "The Data Confidence Score uses a neutral baseline for agency reliability since historical reliability data is not available in PAIMANA."

---

### 01:20 - 01:45 (25 seconds): DCS & Confidence

**Screen:** Project Detail → DCS Section

**What Judge Sees:**
- DCS score (78.5)
- DCS components (completeness, freshness, consistency, reliability)
- Confidence label (MODERATE)
- Warning flags

**What to Say:**
> "The Data Confidence Score breaks down into four components: completeness at 15%, freshness at 25%, consistency at 25%, and reliability at 13.5%. The overall confidence is MODERATE. There's a warning that agency reliability history is not available, so we're using a neutral baseline."

**Data Source:** Computed from real PAIMANA data

**Limitation to Disclose:** Agency reliability baseline

---

### 01:45 - 02:15 (30 seconds): ML Prediction & SHAP

**Screen:** Project Detail → ML Prediction Section

**What Judge Sees:**
- ML prediction probability (11%)
- Predicted class (0 - on time)
- SHAP waterfall chart
- Top 5 feature contributions

**What to Say:**
> "The ML prediction shows an 11% probability of delay, predicting the project will be on time. The SHAP explanation shows the top 5 factors driving this prediction. Original cost, revised cost, and cumulative expenditure are decreasing risk, while physical progress is neutral. 

**Critical Disclosure:**
> "Important: This XGBoost model is experimental and trained on only 160 completed projects. It is not production validated. The predictions are advisory rather than production-certified."

**Data Source:** Real XGBoost model on real PAIMANA data

**Limitation to Disclose:** Experimental ML model, limited training data

---

### 02:15 - 02:45 (30 seconds): Anomalies & RCF

**Screen:** Project Detail → Anomalies Section → RCF Section

**What Judge Sees:**
- Anomaly detection (sudden cost escalation, repeated milestone shifts)
- RCF forecast with fallback warning
- Cost overrun probabilities (P50, P80, P90)

**What to Say:**
> "The Anomaly Detection flagged two critical issues: sudden cost escalation of 79% and repeated milestone shifts with 7 date changes. The Reference Class Forecasting shows cost overrun probabilities - P50 at 18%, P80 at 77%, P90 at 136%.

**Critical Disclosure:**
> "The RCF is using a national-sector fallback because this reference class has fewer than 15 completed projects. This reduces forecast accuracy for projects with sparse reference classes."

**Data Source:** Real PAIMANA historical data

**Limitation to Disclose:** RCF fallback mode, sparse reference classes

---

### 02:45 - 03:15 (30 seconds): PBE & Network

**Screen:** Project Detail → PBE Section → Network Section

**What Judge Sees:**
- PBE percentile (4th percentile)
- Cohort size (1,037 peers)
- Anonymized peer projects
- Network graph with reachability

**What to Say:**
> "The Peer Benchmarking Engine shows this project is at the 4th percentile of 1,037 peers in the same sector and size band. The cost overrun ratio is 179% compared to the peer median of 100%. The Network view shows project reachability based on location and sector relationships.

**Critical Disclosure:**
> "The Network analysis shows reachability based on static relationships, not true risk propagation. It cannot model causal risk spread between projects."

**Data Source:** Real PAIMANA peer projects

**Limitation to Disclose:** Network reachability vs. risk propagation

---

### 03:15 - 03:30 (15 seconds): NID & PDR (Unavailable)

**Screen:** Project Detail → NID Section → PDR Section

**What Judge Sees:**
- NID unavailable with error message
- PDR unavailable with error message

**What to Say:**
> "The Narrative Intelligence Detection is unavailable because PAIMANA source reports do not contain narrative text. Similarly, the Positive Deviance Recommender is unavailable because we need narrative text to extract evidence-backed practices."

**Critical Disclosure:**
> "Current PAIMANA source reports do not contain a usable narrative field, so NID and PDR features are unavailable. This is a data limitation, not a system limitation."

**Data Source:** N/A (unavailable due to data limitation)

**Limitation to Disclose:** 0% narrative coverage in PAIMANA

---

### 03:30 - 04:00 (30 seconds): Governance Review

**Screen:** Governance Queue → Initiate Review → Submit

**What Judge Sees:**
- Governance queue with 336 projects
- Initiate review form
- Justification input
- Submit action

**What to Say:**
> "The Governance Queue shows 336 HIGH+ risk projects requiring review. I'm initiating a review for this project with justification about the cost escalation. The system records the governance action to PostgreSQL for audit trail purposes.

**Critical Disclosure:**
> "This governance workflow is for demonstration only. The system does not have real authority to approve or reject projects. All actions are simulated for the demo."

**Data Source:** Real PAIMANA risk scores, PostgreSQL persistence

**Limitation to Disclose:** Simulated governance, no real authority

---

### 04:00 - 04:25 (25 seconds): Audit Trail

**Screen:** Audit Trail Page

**What Judge Sees:**
- Audit log with recent actions
- Timestamp, user, role, action, entity
- Before/after summaries

**What to Say:**
> "The Audit Trail shows all governance actions with full provenance. Each action includes timestamp, user, role, action type, entity, and before/after summaries. This provides complete accountability for all governance decisions."

**Data Source:** PostgreSQL audit_log table

**Limitation to Disclose:** None for this section

---

### 04:25 - 04:40 (15 seconds): Generate Report

**Screen:** Reports → Generate National Report

**What Judge Sees:**
- Report generation form
- National report with metrics
- Export options (PDF/CSV)

**What to Say:**
> "Finally, I can generate a National Report summarizing all projects, risk distribution, and key metrics. The report includes metadata like timestamp, model version, and data source for full transparency."

**Data Source:** Real PAIMANA database

**Limitation to Disclose:** Reports are on-demand, not real-time

---

### 04:40 - 05:00 (20 seconds): Summary & Q&A

**Screen:** Back to Dashboard

**What to Say:**
> "In summary, PAIMANA AI provides real-time risk intelligence for 2,634 infrastructure projects using real PAIMANA data. The system includes ML predictions with SHAP explanations, reference class forecasting, peer benchmarking, network reachability, and governance workflow - all with explicit disclosure of limitations. The system is advisory, not production-certified, and designed to support decision-making with full transparency."

**Data Source:** All features use real PAIMANA data

**Limitation to Disclose:** Recap key limitations (experimental ML, sparse reference classes, no narrative data)

---

## CRITICAL DISCLOSURE POINTS

### Must Disclose at These Points:

1. **ML/SHAP Section (01:45):**
   - Experimental model status
   - Limited training data (160 projects)
   - Not production validated

2. **RCF Section (02:15):**
   - Fallback mode for sparse reference classes
   - < 15 completed projects triggers fallback

3. **Network Section (02:45):**
   - Reachability only, not risk propagation
   - Static relationships, not dynamic

4. **NID/PDR Section (03:15):**
   - 0% narrative coverage in PAIMANA
   - Data limitation, not system limitation

5. **Governance Section (03:30):**
   - Simulated workflow only
   - No real authority to approve/reject

6. **Summary (04:40):**
   - Advisory nature of predictions
   - Full transparency policy

---

## BACKUP PROJECTS

If the primary project (6e2b1806) has issues, use these backup VERY_HIGH risk projects:

1. **20dc662a-66e8-b474-357f-2320f1f9f671** - Multi-States (Andhra Pradesh, Telangana)
2. **9f4d08cc-3007-4f86-f5ff-9aa95b4d8c8e** - Maharashtra
3. **4eaaad32-ea50-8ec1-f5f4-8c9961bfabf6** - Maharashtra

All have VERY_HIGH risk scores and good demonstration potential.

---

## TECHNICAL SETUP

### Pre-Demo Checklist:
- [ ] Docker containers running (docker ps)
- [ ] PostgreSQL healthy (docker logs infra-db-1)
- [ ] API healthy (curl http://localhost:8001/health)
- [ ] Frontend accessible (http://localhost:5173)
- [ ] Browser console clear (0 errors)
- [ ] Test project ID verified (curl /api/v1/projects/{id}/risk)

### During Demo:
- [ ] Keep to 5-minute timeline
- [ ] Explicitly disclose limitations at each point
- [ ] Use real PAIMANA data only
- [ ] Show PostgreSQL persistence (governance/audit)
- [ ] End with clear summary

---

## CONTINGENCY PLANS

### If API Fails:
- Use cached data in frontend
- Explain API is temporarily unavailable
- Show UI with error handling

### If Database Fails:
- Explain PostgreSQL connection issue
- Show error state in UI
- Restart Docker containers if needed

### If Frontend Fails:
- Check browser console for errors
- Verify Vite dev server running
- Restart frontend container if needed

---

## SUCCESS CRITERIA

The demo is successful if:
- [ ] All sections completed within 5 minutes
- [ ] Real PAIMANA data used throughout
- [ ] All limitations explicitly disclosed
- [ ] PostgreSQL persistence demonstrated
- [ ] No errors or crashes
- [ ] Clear summary provided
- [ ] Judges understand system capabilities and limitations

---

## POST-DEMO Q&A PREPARATION

### Anticipated Questions:

**Q: Is this production-ready?**
A: No, this is a demonstration system. The ML models are experimental and trained on limited data. The system is advisory, not production-certified.

**Q: How accurate are the risk predictions?**
A: The ML models show perfect metrics on a 5-project holdout, but this is not representative of real-world performance. The models are experimental and should be used as advisory tools only.

**Q: Why is NID unavailable?**
A: PAIMANA source reports do not contain narrative text fields. Without narrative data, we cannot perform narrative intelligence detection. This is a data limitation, not a system limitation.

**Q: Can this system approve/reject projects?**
A: No, the governance workflow is for demonstration only. The system does not have real authority to approve or reject projects. All governance actions are simulated.

**Q: How often is the data updated?**
A: The current data is from July 2026, approximately 1 month old. This is a static demonstration with no live data updates.

---

## CONCLUSION

This 5-minute demo flow is designed to showcase PAIMANA AI's key capabilities while maintaining full transparency about limitations. The flow is deterministic, uses real PAIMANA data, and explicitly discloses all experimental features and data limitations.

**Prepared by:** Cascade AI Assistant  
**Date:** August 31, 2026  
**For:** SIH 2026 Judges
