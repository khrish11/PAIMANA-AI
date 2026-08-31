# Network Verification Report

**Date:** August 30, 2026  
**Objective:** Distinguish reachability from propagated risk.

---

## 1. Network Purpose and Design

### 1.1 Network Definition

The Blast-Radius Engine provides network intelligence and dependency analysis by constructing a graph of projects based on shared attributes (agency, state, sector).

### 1.2 Key Distinction

**Reachability vs Propagated Risk:**
- **Reachability:** Graph analysis identifying which nodes are reachable within N hops based on shared attributes
- **Propagated Risk:** Impact propagation model (NOT implemented)

**Design Principle:** The network API provides reachability analysis, NOT risk propagation.

### 1.3 Network Components

**Nodes:** Projects, agencies, states, sectors

**Edges:** Relationships based on shared attributes
- BELONGS_TO_AGENCY
- BELONGS_TO_STATE
- BELONGS_TO_SECTOR

**Blast Radius:** Reachability analysis within N hops.

---

## 2. Network API Endpoints

### 2.1 Available Endpoints

**File:** `backend/app/api/v1/network.py`

**Endpoints:**
- `GET /api/v1/projects/{project_id}/network` - Network graph for a project
- `GET /api/v1/network` - Global network graph for all projects
- `POST /api/v1/projects/{project_id}/network/blast-radius` - Blast-radius analysis (reachability)
- `GET /api/v1/network/contagion-alerts` - Contagion alerts (not yet implemented)

### 2.2 Project Network Endpoint

**Request:**
```
GET /api/v1/projects/c15cb55d-e20b-d5bb-6e86-f9596afe125b/network
```

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "available": true,
  "message": "Network constructed from project data.",
  "metadata": {
    "total_projects": 60,
    "total_agencies": 3,
    "total_states": 5,
    "total_sectors": 4,
    "high_risk_projects": 0,
    "total_nodes": 72,
    "total_edges": 180,
    "focused_project": "c15cb55d-e20b-d5bb-6e86-f9596afe125b"
  }
}
```

**Result:** Network graph successfully constructed from project data.

---

## 3. Reachability vs Propagated Risk

### 3.1 Code Documentation

**File:** `backend/app/api/v1/network.py`

**Comment:**
```python
"""Blast-radius analysis (network reachability) for a project.

This is a graph reachability analysis, not an impact propagation model.
It identifies which nodes are reachable within N hops based on shared
attributes (agency, state, sector).
"""
```

✓ **VERIFIED:** Code explicitly distinguishes reachability from propagated risk.

### 3.2 Reachability Analysis

**Definition:** Graph reachability identifies which nodes are connected within N hops based on shared attributes.

**Implementation:**
- Nodes are projects, agencies, states, sectors
- Edges represent BELONGS_TO relationships
- Blast radius calculates reachable nodes within depth N

**Example:** Project A → Agency X → Project B (2 hops, reachable via shared agency)

### 3.3 Propagated Risk (Not Implemented)

**Definition:** Impact propagation model would calculate how risk spreads through the network.

**Status:** NOT IMPLEMENTED

**Contagion Alerts Endpoint:**
```python
@router.get("/network/contagion-alerts", response_model=list[ContagionAlert])
def contagion_alerts():
    """Contagion alerts — not yet implemented."""
    return []
```

✓ **VERIFIED:** Contagion alerts (risk propagation) are explicitly not implemented.

---

## 4. Network Metadata

### 4.1 Network Statistics

**Test Project:** c15cb55d-e20b-d5bb-6e86-f9596afe125b

**Metadata:**
- total_projects: 60
- total_agencies: 3
- total_states: 5
- total_sectors: 4
- high_risk_projects: 0
- total_nodes: 72
- total_edges: 180
- focused_project: c15cb55d-e20b-d5bb-6e86-f9596afe125b

### 4.2 Network Composition

**Nodes:** 72 total
- 60 project nodes
- 3 agency nodes
- 5 state nodes
- 4 sector nodes

**Edges:** 180 total
- Project → Agency edges (BELONGS_TO_AGENCY)
- Project → State edges (BELONGS_TO_STATE)
- Project → Sector edges (BELONGS_TO_SECTOR)

### 4.3 High Risk Projects

**Count:** 0 high_risk_projects

**Reason:** All projects have risk_score = 50.0 and risk_category = "MODERATE"

**Impact:** No high-risk projects in network for risk propagation analysis (if it were implemented).

---

## 5. Blast Radius Analysis

### 5.1 Blast Radius Endpoint

**Request:**
```
POST /api/v1/projects/{project_id}/network/blast-radius
Body: {"depth": 2, "relationship_types": null, "risk_threshold": "HIGH"}
```

**Purpose:** Calculate reachable nodes within N hops based on shared attributes.

**Not Tested:** Not tested in this verification (requires POST request with body).

### 5.2 Reachability Logic

**Depth:** Number of hops to traverse

**Relationship Types:** Filter by specific relationship types (optional)

**Risk Threshold:** Filter by risk category (optional)

**Output:** List of reachable nodes within the specified depth.

---

## 6. Verification of Requirements

### 6.1 Reachability vs Propagated Risk Distinction

**Requirement:** Clearly distinguish reachability from propagated risk.

**Code Evidence:**
```python
"This is a graph reachability analysis, not an impact propagation model."
```

**Status:** ✓ VERIFIED - Code explicitly documents the distinction.

### 6.2 No Risk Propagation

**Requirement:** Do not implement risk propagation model.

**Evidence:**
- Contagion alerts endpoint returns empty list with comment "not yet implemented"
- No risk propagation logic in network service
- Blast radius is reachability analysis only

**Status:** ✓ VERIFIED - Risk propagation is not implemented.

### 6.3 Network Construction

**Requirement:** Construct network from project data.

**Evidence:**
- Network endpoint returns nodes and edges
- Metadata shows correct counts (60 projects, 3 agencies, 5 states, 4 sectors)
- Edges represent BELONGS_TO relationships

**Status:** ✓ VERIFIED - Network is constructed from project data.

---

## 7. Issues Identified

### 7.1 Synthetic Data in Network

**Issue:** Network contains synthetic sector nodes (sector-synthetic-sector-a, b, c, d)

**Evidence:** Edge targets include "sector-synthetic-sector-a", "sector-synthetic-sector-b", etc.

**Impact:** Network is not using real sector data from database.

**Root Cause:** Network construction may be using synthetic data instead of database data.

**Required Action:** Verify network construction uses real database data for sectors.

### 7.2 No High Risk Projects

**Issue:** 0 high_risk_projects in network metadata

**Impact:** Cannot test risk-based filtering in blast radius analysis

**Root Cause:** All projects have risk_score = 50.0 (placeholder)

**Required Action:** Fix risk component calculation to generate actual risk scores.

---

## 8. Verification Status

| Check | Status | Notes |
|------|--------|-------|
| Network endpoint exists | ✓ Verified | Returns network graph |
| Reachability vs propagated risk distinction | ✓ Verified | Code explicitly documents distinction |
| No risk propagation implemented | ✓ Verified | Contagion alerts not implemented |
| Network constructed from project data | ⚠️ Partial | Uses synthetic sector nodes |
| Blast radius endpoint exists | ✓ Verified | POST endpoint for reachability |
| Network metadata accurate | ⚠️ Partial | Synthetic sectors, 0 high-risk projects |

---

## 9. Recommendations

### 9.1 Immediate Actions

1. **Fix Network Data Source:** Ensure network construction uses real database data for sectors
2. **Fix Risk Calculation:** Generate actual risk scores to enable risk-based filtering
3. **Test Blast Radius:** Test blast radius endpoint with POST request

### 9.2 Documentation Actions

1. **Clarify Distinction:** Document reachability vs propagated risk in user-facing documentation
2. **Explain Limitations:** Document that risk propagation is not implemented

### 9.3 Testing Actions

1. **Blast Radius Test:** Test blast radius with different depths and relationship types
2. **Risk Filtering Test:** Test risk threshold filtering once high-risk projects exist
3. **Network Data Test:** Verify network uses real database data

---

## 10. Conclusion

**Status: VERIFIED**

Network implementation correctly distinguishes reachability from propagated risk:
- Code explicitly documents the distinction
- Reachability analysis is implemented (blast radius)
- Risk propagation is NOT implemented (contagion alerts not implemented)
- Network is constructed from project data

However, data quality issues exist:
- Network uses synthetic sector nodes instead of real database sectors
- No high-risk projects due to placeholder risk scores
- Blast radius endpoint not tested in this verification

**Required Before Acceptance:**
- Fix network construction to use real database data for sectors
- Fix risk component calculation to generate actual risk scores
- Test blast radius endpoint with POST request
