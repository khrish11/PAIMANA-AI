# Positive Deviance Radar (PDR)

## Overview

The Positive Deviance Radar (PDR) is an evidence-based system that identifies projects performing significantly better than their reference class peers, extracts successful practices from their narrative reports, clusters these practices into evidence-backed playbooks, and recommends relevant playbooks to struggling projects.

## Implementation Status

### ✅ Completed Components

**Backend Services:**
- ✅ `positive_deviance.py` - Detects projects performing better than reference class peers using residual z-scores with DCS guardrails
- ✅ `playbook_extraction.py` - Extracts concrete actions from narratives using Ollama/NID infrastructure with specificity filtering
- ✅ `playbook_clustering.py` - Clusters actions into playbooks using sentence-transformers (with deterministic fallback)
- ✅ `playbook_matching.py` - Matches playbooks to struggling projects based on SHAP drivers and risk triggers

**Database:**
- ✅ 4 new ORM models: `PositiveDeviant`, `ExtractedAction`, `Playbook`, `PlaybookSuggestion`
- ✅ Alembic migration `0002_positive_deviance_radar.py` with all tables, indexes, and constraints
- ✅ Updated `models/__init__.py` exports

**API:**
- ✅ `positive_deviance.py` router with endpoints for deviants, playbooks, suggestions, and user actions
- ✅ Pydantic schemas for all PDR responses
- ✅ Router registered in `main.py`

**Frontend:**
- ✅ API client methods in `api.js` for all PDR endpoints
- ✅ `usePositiveDeviance` hook with caching and error handling
- ✅ 4 React components: `PlaybookCard`, `PlaybookLibrary`, `PlaybookEvidence`, `PositiveDeviantBadge`
- ✅ Integration into Project Detail page with "Recommended Practices" section
- ✅ 2 new pages: `/positive-deviance` and `/playbooks`
- ✅ Routes added to `App.jsx`

**Testing:**
- ✅ Backend tests: `test_positive_deviance.py`, `test_playbook_extraction.py`, `test_playbook_clustering.py`, `test_playbook_matching.py`, `test_positive_deviance_api.py`
- ✅ Frontend tests: `PlaybookCard.test.jsx`, `PlaybookEvidence.test.jsx`, `PositiveDeviantBadge.test.jsx`, `PlaybookLibrary.test.jsx`, `PositiveDeviance.test.jsx`
- ✅ Vitest configuration added
- ✅ ESLint configuration added

**Scheduler:**
- ✅ APScheduler monthly workflow implemented in `scheduler.py`
- ✅ Jobs: detect_positive_deviants, extract_narrative_actions, cluster_playbooks, refresh_suggestions
- ✅ Idempotent job design to prevent duplicates
- ✅ Integrated with FastAPI lifespan context manager

**Synthetic Demo:**
- ✅ Synthetic PDR fixture in `data/synthetic/pdr/`
- ✅ 3 positive deviant projects (A, B, C) with same action pattern
- ✅ 1 struggling project (D) with risk trigger
- ✅ Clear labeling as "SYNTHETIC DATA — FOR TESTING ONLY"

**Environment:**
- ✅ Fixed pandas/Meson installation issue (updated to pandas>=2.2.3)
- ✅ Updated psycopg[binary] to 3.2.13 for Python 3.13 compatibility
- ✅ Fixed SQLAlchemy import issues in PDR models (DateTime, Index)
- ✅ Backend app imports successfully
- ✅ Frontend build passes

### ⚠️ Pending Items (Require Database Connection)

**Database Migration:**
- ⚠️ Migration `0002_positive_deviance_radar.py` created but not executed (requires PostgreSQL connection)
- ⚠️ PostgreSQL authentication issue: password authentication failed for user "paimana"

**API Verification:**
- ⚠️ PDR API endpoints created but not verified with live database
- ⚠️ Endpoints: `/api/v1/positive-deviants`, `/api/v1/playbooks`, `/api/v1/projects/{id}/suggested-playbooks`

**Full System Test:**
- ⚠️ Backend pytest cannot run without database connection
- ⚠️ Frontend tests require npm install of new dependencies

### 🔧 Known Issues

**Database Connection:**
- PostgreSQL authentication failure for user "paimana"
- Requires database setup/credentials configuration before migration and testing can proceed

**Frontend Test Dependencies:**
- New testing dependencies (vitest, @testing-library/*, eslint) need to be installed
- Run: `cd frontend && npm install`

## Definition of Positive Deviance

A **positive deviant** is a project that performs materially better than its reference class peers while operating under similar conditions. This is determined through statistical comparison of cost and schedule performance against reference class baselines.

## Deviance Formula

For each project/month, we calculate:

```
residual_cost = project.cost_overrun_ratio - reference_class.cost_overrun_p50
residual_schedule = project.schedule_slip_months - reference_class.schedule_delay_p50
```

These residuals are converted to z-scores using the reference class distribution statistics. A project is a positive deviant when both residuals are negative (better than average) and exceed a configurable threshold.

## DCS Guardrail

A project can only become a positive deviant if its Data Confidence Score (DCS) meets the minimum threshold:

- **MIN_DCS = 70**

Projects with DCS below this threshold are excluded because their data is insufficiently trustworthy for playbook extraction.

## LLM Extraction

For each detected positive deviant, we extract concrete successful actions from narrative reports using the existing Ollama/NID infrastructure.

### Extraction Process

1. **Input**: Last 6 months of narrative text for a positive deviant
2. **LLM**: Uses structured output to extract actions with:
   - action_text
   - category (land_acquisition, procurement, contractor_management, design_change, stakeholder_coordination, resource_planning, other)
   - source_month
   - quote_evidence
   - specificity_score (1-5)
3. **Filter**: Only retains actions with specificity_score >= 3
4. **Logging**: Records prompt version, model version, project/deviant ID, timestamp, extraction status, and raw output

### Malformed Output Handling

If LLM output is malformed or cannot be parsed:
- Status is set to `extraction_unavailable`
- No fake empty action list is created
- Error is logged for audit trail

## Clustering

Extracted actions are clustered into playbooks using:

### Embedding Approach (Preferred)
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Similarity: Cosine similarity
- Clustering: Agglomerative clustering or DBSCAN
- Threshold: 0.75 similarity

### Fallback Approach
- If sentence-transformers is unavailable
- Uses deterministic text similarity (SequenceMatcher)
- Threshold: 0.7 similarity
- Marked as fallback in playbook metadata

### Hard Guardrail

**A playbook MUST contain actions from >= 3 DIFFERENT PROJECTS**

This is a non-negotiable requirement. Playbooks from single projects are never created.

## Minimum Evidence Requirement

Each playbook must:
- Contain actions from at least 3 independent source projects
- Have actions in the same category
- Pass the similarity threshold for clustering

## Confidence Tiers

Confidence is based on the number of independent source projects:

- **LOW**: 3 projects
- **MEDIUM**: 4-6 projects
- **HIGH**: 7+ projects

## Matching

Playbooks are matched to struggling projects when:

### Trigger Condition
- Composite risk >= MODERATE

### Matching Process
1. Extract SHAP feature categories from risk drivers
2. Map SHAP features to playbook categories:
   - land-related → land_acquisition
   - contractor-related → contractor_management
   - schedule/resource → resource_planning
   - procurement → procurement
   - design → design_change
   - stakeholder → stakeholder_coordination
3. Query MEDIUM and HIGH confidence playbooks first
4. Rank by:
   - Category relevance (40%)
   - Reference class compatibility (20%)
   - PBE profile similarity (20%)
   - Source project count (20%)
5. Return top 1-3 suggestions

## Limitations

1. **Not Causal**: Playbooks are evidence-backed patterns, not causal recommendations. The system does not claim that the playbook caused the positive outcome.

2. **Data Dependent**: Requires sufficient narrative data for extraction and sufficient project count for clustering.

3. **Reference Class Quality**: Dependent on reference class having adequate sample size (>=15 projects).

4. **LLM Reliability**: Extraction quality depends on LLM performance and narrative quality.

5. **Human-in-the-Loop**: PDR is advisory only. Final decisions belong to authorized human reviewers.

## Human-in-the-Loop

PDR is designed as an advisory system:

- **Never** automatically modifies a project
- **Never** automatically changes risk scores
- **Never** automatically approves/rejects funding
- **Never** automatically executes interventions

A playbook is a **RECOMMENDATION ONLY**. The final decision belongs to the authorized human reviewer.

## Evidence Transparency

Every playbook must answer "WHY IS THIS A PLAYBOOK?" by showing:

- Number of independent source projects
- Source project sectors
- Source project reference classes (where safe)
- Confidence tier
- Extracted action count
- Evidence quotes from narrative reports
- Source months for each action

The system never simply says "AI recommends this." Users must see the supporting evidence.

## Scheduling

### Monthly Jobs
- Detect positive deviants
- Extract actions for new deviants
- Rebuild playbook clusters
- Refresh suggestions

### On-Demand
- Project-level suggestion retrieval

Clustering and LLM extraction run as background jobs to avoid blocking API requests.

## Performance Considerations

- Backend filtering/pagination for large datasets
- Caching of playbook library and suggestions
- Background jobs for embedding, clustering, and LLM extraction
- No sending entire PAIMANA dataset to browser

## API Endpoints

### GET /api/v1/positive-deviants
List current positive deviants with optional filters (sector, state).

**Access**: IPMD, Analyst

### GET /api/v1/playbooks
List available playbooks with optional filters (category, confidence_tier).

**Access**: IPMD, Analyst

### GET /api/v1/playbooks/{playbook_id}
Get detailed playbook with evidence actions and quotes.

**Access**: IPMD, Analyst

### GET /api/v1/projects/{id}/suggested-playbooks
Get suggested playbooks for a project.

**Access**:
- Agency: own project only
- IPMD/Analyst: all permitted projects

### POST /api/v1/projects/{id}/suggested-playbooks/{suggestion_id}/dismiss
Dismiss a playbook suggestion. Records audit event.

### POST /api/v1/projects/{id}/suggested-playbooks/{suggestion_id}/viewed
Mark a playbook suggestion as viewed.

## Frontend Pages

### /positive-deviance
Positive Deviance Radar page showing:
- Positive deviant count
- Sectors, states, reference classes
- DCS distribution
- Table of positive deviants with performance residuals
- Methodology explanation

### /playbooks
Playbook Library page (Analyst/IPMD only) with:
- Filters by category, confidence tier, sector, source project count
- Playbook cards with evidence
- Links to full playbook details

### /projects/:id (Project Detail)
Integrated "Recommended Practices" section showing:
- Playbook suggestions when available
- Evidence quotes
- Source project count
- Why recommended (trigger reason)
- Dismiss button

## Configurable Settings

### Backend
- `MIN_TRACK_RECORD = 6` (minimum months of data)
- `MIN_DCS = 70` (minimum data confidence score)
- `DEVIANCE_THRESHOLD = -1.5` (z-score threshold)
- `THRESHOLD_METHOD = 'zscore'` (or 'percentile')
- `MIN_SPECIFICITY_SCORE = 3` (for action extraction)
- `MIN_INDEPENDENT_PROJECTS = 3` (for playbook creation)
- `SIMILARITY_THRESHOLD = 0.7` (fallback clustering)
- `EMBEDDING_THRESHOLD = 0.75` (embedding clustering)

### LLM
- `PROMPT_VERSION = 'v1'`
- `MODEL_VERSION = 'llama3.2'` (configurable)

## Database Tables

### positive_deviants
- deviant_id (UUID PK)
- project_id (UUID FK)
- reference_class_id (UUID FK)
- reporting_month (DATE)
- residual_cost_zscore (FLOAT)
- residual_schedule_zscore (FLOAT)
- data_confidence_score (FLOAT)
- detected_at (TIMESTAMP)

### extracted_actions
- action_id (UUID PK)
- deviant_id (UUID FK)
- project_id (UUID FK)
- action_text (TEXT)
- category (STRING)
- source_month (STRING)
- quote_evidence (TEXT)
- specificity_score (INTEGER)
- llm_model_version (STRING)
- prompt_version (STRING)
- extracted_at (TIMESTAMP)

### playbooks
- playbook_id (UUID PK)
- category (STRING)
- label (STRING)
- confidence_tier (STRING)
- source_action_ids (UUID ARRAY)
- source_project_count (INTEGER)
- created_at (TIMESTAMP)
- last_updated_at (TIMESTAMP)

### playbook_suggestions
- suggestion_id (UUID PK)
- project_id (UUID FK)
- playbook_id (UUID FK)
- triggered_by_risk_category (STRING)
- suggested_at (TIMESTAMP)
- was_viewed (BOOLEAN)
- was_dismissed (BOOLEAN)

## Integration Points

### Existing Infrastructure
- **RCF**: Reference class statistics for deviance calculation
- **DCS**: Data confidence guardrail
- **SHAP**: Risk driver extraction for matching
- **PBE**: Profile similarity for ranking
- **NID**: Ollama infrastructure for LLM extraction
- **Risk Scoring**: Trigger condition (composite risk >= MODERATE)

### No New Infrastructure
- Reuses existing Ollama connection
- Reuses existing RCF clusters
- Reuses existing PBE similarity/profile logic
