# Critical Limitations - SIH 2026 Demo

**Date:** August 31, 2026  
**Purpose:** Explicit disclosure of all system limitations for SIH 2026 judges  
**Status:** All limitations must be disclosed honestly

---

## 1. SECTOR COVERAGE LIMITATION

### Issue
- **Unknown Sector:** Many projects in the PAIMANA database have "Unknown" sector classification
- **Sector Imbalance:** Distribution of projects across sectors is highly uneven
- **Impact:** Limited ability to perform sector-specific analysis for unknown sectors

### Data Evidence
- **Total Projects:** 2,634
- **Unknown Sector:** Significant portion (exact count varies by reporting period)
- **Well-Represented Sectors:** Road Transport, Power, Healthcare have better coverage

### Disclosure to Judges
> "Many projects in the PAIMANA database have unknown sector classification, which limits our ability to perform sector-specific risk analysis for those projects. The system defaults to national-level benchmarks when sector information is unavailable."

---

## 2. MINISTRY COVERAGE LIMITATION

### Issue
- **Empty Ministry Fields:** Some projects have empty ministry fields
- **Ministry Imbalance:** Distribution skewed toward certain ministries (e.g., Ministry of Road Transport & Highways)
- **Impact:** Limited ministry-level governance insights

### Data Evidence
- **Empty Ministry Fields:** Present in project data
- **Well-Represented Ministries:** Road Transport & Highways, Power, Health
- **Under-Represented Ministries:** Various smaller ministries

### Disclosure to Judges
> "Ministry coverage is uneven across the PAIMANA database. Some projects have empty ministry fields, and certain ministries are significantly under-represented, which limits the granularity of ministry-level governance insights."

---

## 3. NARRATIVE/NID LIMITATION

### Issue
- **0% Narrative Coverage:** PAIMANA source reports do not contain usable narrative fields
- **NID Unavailable:** Narrative Intelligence Detection cannot function without narrative text
- **Impact:** No narrative-based insights, contradictions, or evidence extraction

### Data Evidence
- **Narrative Fields:** Absent or empty in PAIMANA source
- **NID Status:** Explicitly unavailable for all projects
- **Error Message:** "No narrative text available for NID analysis"

### Disclosure to Judges
> "Current PAIMANA source reports do not contain a usable narrative field. As a result, the Narrative Intelligence Detection (NID) feature is unavailable for all projects. This limits our ability to extract narrative-based insights, identify contradictions, and perform text analysis."

---

## 4. PROJECT STATUS LIMITATION

### Issue
- **Limited Completed Outcomes:** Only 160 projects have completed status
- **Status Imbalance:** Most projects are "Active" with unknown completion status
- **Impact:** Limited training data for ML models, biased performance estimates

### Data Evidence
- **Completed Projects:** 160 out of 2,634 (6%)
- **Active Projects:** Majority of projects
- **Unknown Completion:** Many projects lack completion status

### Disclosure to Judges
> "Only 160 projects (6%) in the PAIMANA database have completed status. The majority are marked as 'Active' with unknown completion outcomes. This limits the training data available for ML models and may bias performance estimates toward active projects."

---

## 5. EXPERIMENTAL ML LIMITATION

### Issue
- **Experimental Status:** XGBoost and Random Forest models are experimental
- **Limited Training Data:** Only 160 completed projects for training
- **Not Production Validated:** Models have not been validated for production use
- **Impact:** Risk predictions are advisory, not production-certified

### Data Evidence
- **Training Period:** January 2024 to June 2026
- **Validation Period:** July 2026 (5 projects only)
- **Model Status:** Marked as "EXPERIMENTAL" in UI
- **Performance Metrics:** Perfect metrics on tiny holdout (not representative)

### Disclosure to Judges
> "The XGBoost and Random Forest models are experimental and trained on only 160 completed projects. They have not been validated for production use. Risk predictions shown are advisory rather than production-certified. The perfect performance metrics on the 5-project holdout are not representative of real-world performance."

---

## 6. RCF SPARSE-REFERENCE LIMITATION

### Issue
- **Sparse Reference Classes:** Many reference classes have fewer than 15 completed projects
- **Fallback Mode:** System uses national-sector fallback when reference class is insufficient
- **Impact:** Less accurate forecasts for projects with sparse reference classes

### Data Evidence
- **Reference Class Size:** Varies widely (some < 15, some > 100)
- **Fallback Trigger:** < 15 completed projects in reference class
- **Warning Message:** "Reference-class cluster below 15 completed projects; using national-sector fallback"

### Disclosure to Judges
> "Reference Class Forecasting (RCF) requires at least 15 completed projects in a reference class for accurate forecasting. Many reference classes in the PAIMANA database have fewer than 15 completed projects, so the system falls back to national-sector benchmarks. This reduces forecast accuracy for projects with sparse reference classes."

---

## 7. PDR EVIDENCE LIMITATION

### Issue
- **No Narrative Data:** PDR requires narrative text for action extraction
- **No Evidence-Backed Playbooks:** Without narratives, no evidence-backed playbooks can be generated
- **Impact:** PDR feature unavailable, no practice recommendations

### Data Evidence
- **Narrative Coverage:** 0% in PAIMANA data
- **Playbooks:** 0 evidence-backed playbooks available
- **PDR Status:** Explicitly unavailable

### Disclosure to Judges
> "Positive Deviance Recommender (PDR) requires narrative text to extract evidence-backed practices. Since PAIMANA source reports do not contain narrative fields, no evidence-backed playbooks are available. The PDR feature is explicitly unavailable with a clear explanation."

---

## 8. NETWORK REACHABILITY LIMITATION

### Issue
- **Reachability Only:** Network analysis shows project reachability, not true risk propagation
- **Static Relationships:** Based on current project attributes, not dynamic interactions
- **Impact:** Cannot model true risk contagion or propagation

### Data Evidence
- **Network Type:** Static graph based on project attributes
- **Relationship Type:** LOCATED_IN (project to state/sector)
- **Analysis:** Blast radius and reachability, not propagation

### Disclosure to Judges
> "The Network feature shows project reachability based on static relationships (e.g., projects located in the same state or sector). It does not model true risk propagation or contagion. The analysis is based on current project attributes and does not capture dynamic interactions or causal risk spread."

---

## 9. LIGHTGBM LIMITATION

### Issue
- **Library Dependency:** LightGBM requires libgomp.so.1 library
- **Missing Dependency:** Library not available in Docker container
- **Impact:** LightGBM model unavailable

### Data Evidence
- **Error Message:** "libgomp.so.1: cannot open shared object file: No such file or directory"
- **Model Status:** Unavailable
- **Alternative:** XGBoost and Random Forest available

### Disclosure to Judges
> "The LightGBM model is unavailable due to a missing library dependency (libgomp.so.1) in the Docker container. XGBoost and Random Forest models are available as alternatives for ML-based risk prediction."

---

## 10. HOLDOUT SIZE LIMITATION

### Issue
- **Tiny Holdout:** Only 5 projects in validation holdout
- **Unrepresentative Metrics:** Performance metrics on 5 projects not representative
- **Impact:** Over-optimistic performance estimates

### Data Evidence
- **Holdout Size:** 5 projects (July 2026)
- **Performance Metrics:** Perfect metrics (F1=1.0, ROC-AUC=1.0)
- **Representativeness:** Not representative of real-world performance

### Disclosure to Judges
> "The validation holdout contains only 5 projects (July 2026 data). Performance metrics on this tiny holdout (F1=1.0, ROC-AUC=1.0) are not representative of real-world performance and should be interpreted with extreme caution. The perfect metrics are an artifact of the small holdout size."

---

## 11. DATA FRESHNESS LIMITATION

### Issue
- **Data Age:** Data is ~1 month old (July 2026)
- **Static Demo:** No live data updates during demonstration
- **Impact:** May not reflect most recent project status

### Data Evidence
- **Last Import:** August 2026
- **Reporting Period:** July 2025 to July 2026
- **Data Age:** ~1 month at time of demo

### Disclosure to Judges
> "The PAIMANA data used in this demonstration was imported in August 2026 and covers the period from July 2025 to July 2026. The data is approximately 1 month old and does not reflect the most recent project status or submissions. This is a static demonstration with no live data updates."

---

## 12. GOVERNANCE WORKFLOW LIMITATION

### Issue
- **Demo Governance:** Governance actions are for demonstration only
- **No Real Authority:** System does not have authority to approve/reject projects
- **Impact:** Governance workflow is simulated, not real

### Data Evidence
- **Governance Actions:** 0 real governance actions in database
- **Test Records:** 8 test audit events only
- **Authority:** System is advisory, not authoritative

### Disclosure to Judges
> "The Governance workflow is for demonstration purposes only. The system does not have real authority to approve, reject, or reallocate funding for projects. All governance actions shown are simulated for the demonstration and do not represent actual government decisions."

---

## 13. AGENCY RELIABILITY LIMITATION

### Issue
- **No Reliability History:** Agency reliability history not available in PAIMANA
- **Neutral Baseline:** DCS reliability component scored at neutral baseline
- **Impact:** DCS scores may overestimate data quality

### Data Evidence
- **Reliability History:** Not available in PAIMANA source
- **DCS Warning:** "Agency reliability history not available; scored at neutral baseline"
- **Impact:** Reduced accuracy of DCS reliability component

### Disclosure to Judges
> "Agency reliability history is not available in the PAIMANA database. The Data Confidence Score (DCS) reliability component is scored at a neutral baseline, which may overestimate actual data quality for agencies with poor reporting history."

---

## 14. ANOMALY DETECTION LIMITATION

### Issue
- **Rule-Based Detection:** Anomaly detection uses simple rule-based thresholds
- **Limited Context:** Does not consider project-specific context
- **Impact:** May generate false positives or miss nuanced anomalies

### Data Evidence
- **Detection Method:** Rule-based thresholds (e.g., cost escalation > 50%)
- **Context:** Limited project-specific context
- **False Positives:** Possible due to simple rules

### Disclosure to Judges
> "Anomaly detection uses simple rule-based thresholds (e.g., cost escalation > 50%) without considering project-specific context. This may generate false positives for legitimate project changes or miss nuanced anomalies that require contextual understanding."

---

## 15. REPORTING LIMITATION

### Issue
- **Static Reports:** Reports are generated on-demand, not real-time
- **Limited Export:** PDF/CSV/XLSX export where implemented
- **Impact:** Reports may not reflect latest data

### Data Evidence
- **Report Generation:** On-demand based on current database state
- **Export Status:** Partially implemented
- **Real-Time:** Not real-time

### Disclosure to Judges
> "Reports are generated on-demand based on the current database state and are not real-time. PDF/CSV/XLSX export is implemented where available. Reports may not reflect the most recent data if the database has been updated."

---

## SUMMARY OF CRITICAL LIMITATIONS

### Must Disclose to Judges
1. **Sector Coverage:** Unknown sectors limit sector-specific analysis
2. **Ministry Coverage:** Empty fields limit ministry-level insights
3. **Narrative Coverage:** 0% coverage makes NID unavailable
4. **Project Status:** Limited completed outcomes bias ML models
5. **ML Models:** Experimental, not production validated
6. **RCF:** Sparse reference classes require fallback
7. **PDR:** No evidence-backed playbooks available
8. **Network:** Reachability only, not risk propagation
9. **LightGBM:** Unavailable due to library dependency
10. **Holdout Size:** Tiny holdout inflates performance metrics
11. **Data Freshness:** 1-month-old data, static demo
12. **Governance:** Simulated workflow, no real authority
13. **Agency Reliability:** No history, neutral baseline
14. **Anomaly Detection:** Rule-based, limited context
15. **Reporting:** On-demand, not real-time

### Honest Disclosure Policy
- **All Limitations:** Explicitly disclosed in UI
- **Experimental Features:** Clearly marked
- **Unavailable Features:** Honest error states with explanations
- **No Synthetic Data:** Real PAIMANA data only
- **No Overclaiming:** Advisory nature of predictions emphasized

---

## DEMO SCRIPT INTEGRATION

All limitations must be disclosed at appropriate points in the demo script:

- **ML/SHAP Section:** Disclose experimental status and limited training data
- **RCF Section:** Disclose fallback mode for sparse reference classes
- **NID Section:** Disclose 0% narrative coverage
- **PDR Section:** Disclose no evidence-backed playbooks
- **Network Section:** Disclose reachability vs. risk propagation
- **Governance Section:** Disclose simulated workflow
- **Dashboard Section:** Disclose data freshness and sector/ministry limitations

---

## CONCLUSION

The PAIMANA AI system has several critical limitations that must be honestly disclosed to SIH 2026 judges. These limitations are inherent to the available PAIMANA data and the experimental nature of the ML models. The system is designed to provide advisory insights rather than production-certified predictions, and all limitations are explicitly disclosed in the UI and documentation.

**Transparency Policy:** Full disclosure of all limitations, no overclaiming, honest error states for unavailable features.

**Prepared by:** Cascade AI Assistant  
**Date:** August 31, 2026  
**For:** SIH 2026 Judges
