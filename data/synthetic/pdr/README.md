# SYNTHETIC PDR DEMO DATA

**SYNTHETIC DATA — FOR TESTING ONLY**

This directory contains synthetic test data for Positive Deviance Radar (PDR) integration testing and demonstration purposes only.

**DO NOT** use this data for:
- Production model training
- Real project evaluation
- Performance benchmarking
- Any decision-making

This data is fabricated to test the complete PDR pipeline:
1. Positive deviant detection
2. Narrative extraction
3. Action clustering
4. Playbook generation
5. Suggestion matching

## Test Scenario

### Positive Deviant Projects (3 projects)

All three projects describe variations of the same concrete action:
"Weekly direct coordination with district administration reduced land-acquisition delays."

**Project A (Highway Project Alpha)**
- Sector: Roads
- State: Uttar Pradesh
- Reference Class: Roads-Large-North
- DCS: 85
- Months Tracked: 12
- Performance: Better than reference class (negative residuals)
- Narrative: Describes weekly coordination with district administration

**Project B (Highway Project Beta)**
- Sector: Roads
- State: Bihar
- Reference Class: Roads-Large-North
- DCS: 82
- Months Tracked: 14
- Performance: Better than reference class (negative residuals)
- Narrative: Describes regular meetings with district collector

**Project C (Highway Project Gamma)**
- Sector: Roads
- State: Madhya Pradesh
- Reference Class: Roads-Large-North
- DCS: 88
- Months Tracked: 10
- Performance: Better than reference class (negative residuals)
- Narrative: Describes direct coordination with district administration

### Struggling Project (1 project)

**Project D (Highway Project Delta)**
- Sector: Roads
- State: Uttar Pradesh
- Reference Class: Roads-Large-North
- Risk Category: MODERATE
- SHAP Driver: land_related_delay
- Expected: Receives playbook suggestion

## Expected Pipeline Flow

```
Project A, B, C (Positive Deviants)
  ↓
Narrative Extraction (LLM)
  ↓
Action Extraction (same action cluster)
  ↓
Playbook Clustering (3 independent projects)
  ↓
MEDIUM-confidence playbook
  ↓
Project D (Struggling)
  ↓
Risk/SHAP category match
  ↓
Suggested playbook
```

## Usage

This fixture is used for:
- Integration testing of the complete PDR pipeline
- Demo purposes to show playbook suggestion flow
- Verification of clustering logic (>=3 independent projects)

## Safety

All synthetic data is clearly labeled with:
- "SYNTHETIC DATA — FOR TESTING ONLY" banners
- Isolated directory structure
- Never mixed with real PAIMANA data
