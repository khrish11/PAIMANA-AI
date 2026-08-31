"""Network Intelligence Service - constructs project dependency graphs.

This service builds network graphs from project data to support:
- Project dependency visualization
- Agency/state/sector relationship mapping
- Network reach analysis
- Blast-radius calculation

The network is constructed from actual project attributes:
- Projects as primary nodes
- Agencies, states, sectors as relationship nodes
- Edges based on shared attributes (agency, state, sector)

No fabricated dependencies or relationships are created.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.projects import Project
from app.models.risk_scores import RiskScore
from app.schemas.schemas import NetworkNode, NetworkEdge, NetworkResponse, RiskCategory

logger = logging.getLogger(__name__)


def _get_risk_category(score: float) -> RiskCategory:
    """Convert risk score to RiskCategory enum."""
    if score >= 75:
        return RiskCategory.CRITICAL
    if score >= 60:
        return RiskCategory.VERY_HIGH
    if score >= 45:
        return RiskCategory.HIGH
    if score >= 30:
        return RiskCategory.MODERATE
    return RiskCategory.LOW


def build_project_network(project_id: str | None = None) -> NetworkResponse:
    """Build a network graph from project data.
    
    Args:
        project_id: Optional project ID to focus the network around. If None,
                  returns the full national network.
    
    Returns:
        NetworkResponse with nodes, edges, and metadata.
    """
    session = SessionLocal()
    
    try:
        # Query projects from PostgreSQL
        projects_query = session.query(Project).all()
        
        if not projects_query:
            return NetworkResponse(
                available=False,
                message="No project data available for network construction.",
                nodes=[],
                edges=[]
            )
        
        # Get latest risk scores for all projects
        risk_scores = {}
        latest_risks = session.query(
            RiskScore.project_id,
            RiskScore.composite_score
        ).distinct(RiskScore.project_id).order_by(
            RiskScore.project_id,
            RiskScore.reporting_month.desc()
        ).all()
        
        for rs in latest_risks:
            risk_scores[rs.project_id] = float(rs.composite_score) if rs.composite_score else 0.0
        
        # Build nodes
        nodes: list[NetworkNode] = []
        edges: list[NetworkEdge] = []
        
        # Track unique agencies, states, sectors
        agencies = set()
        states = set()
        sectors = set()
        
        # Build project nodes first
        project_map = {}  # project_id -> node data
        
        for proj in projects_query:
            proj_id = str(proj.project_id)  # Convert UUID to string
            risk_score = risk_scores.get(proj_id, 0.0)
            
            node = NetworkNode(
                id=proj_id,
                label=proj_id,  # Project model doesn't have project_name field
                node_type="PROJECT",
                risk_category=_get_risk_category(risk_score),
                value=risk_score
            )
            nodes.append(node)
            project_map[proj_id] = {
                "node": node,
                "agency": proj.ministry or "Unknown",
                "state": proj.state or "Unknown",
                "sector": proj.sector or "Unknown",
                "status": proj.status or "unknown"
            }
            
            # Collect unique attributes
            agencies.add(proj.ministry or "Unknown")
            states.add(proj.state or "Unknown")
            sectors.add(proj.sector or "Unknown")
        
        # Build agency nodes
        agency_nodes = {}
        for agency in agencies:
            if agency == "Unknown":
                continue
            node_id = f"agency-{agency.lower().replace(' ', '-')}"
            node = NetworkNode(
                id=node_id,
                label=agency,
                node_type="AGENCY",
                risk_category=None,
                value=0
            )
            nodes.append(node)
            agency_nodes[agency] = node_id
        
        # Build state nodes
        state_nodes = {}
        for state in states:
            if state == "Unknown":
                continue
            node_id = f"state-{state.lower().replace(' ', '-')}"
            node = NetworkNode(
                id=node_id,
                label=state,
                node_type="STATE",
                risk_category=None,
                value=0
            )
            nodes.append(node)
            state_nodes[state] = node_id
        
        # Build sector nodes
        sector_nodes = {}
        for sector in sectors:
            if sector == "Unknown":
                continue
            node_id = f"sector-{sector.lower().replace(' ', '-')}"
            node = NetworkNode(
                id=node_id,
                label=sector,
                node_type="SECTOR",
                risk_category=None,
                value=0
            )
            nodes.append(node)
            sector_nodes[sector] = node_id
        
        # Build edges based on relationships
        edge_id_counter = 0
        
        # Project -> Agency edges
        for proj_id, proj_data in project_map.items():
            agency = proj_data["agency"]
            if agency in agency_nodes:
                edge = NetworkEdge(
                    source=proj_id,
                    target=agency_nodes[agency],
                    relationship_type="FUNDED_BY",
                    weight=1.0
                )
                edges.append(edge)
                edge_id_counter += 1
        
        # Project -> State edges
        for proj_id, proj_data in project_map.items():
            state = proj_data["state"]
            if state in state_nodes:
                edge = NetworkEdge(
                    source=proj_id,
                    target=state_nodes[state],
                    relationship_type="LOCATED_IN",
                    weight=1.0
                )
                edges.append(edge)
                edge_id_counter += 1
        
        # Project -> Sector edges
        for proj_id, proj_data in project_map.items():
            sector = proj_data["sector"]
            if sector in sector_nodes:
                edge = NetworkEdge(
                    source=proj_id,
                    target=sector_nodes[sector],
                    relationship_type="BELONGS_TO_SECTOR",
                    weight=1.0
                )
                edges.append(edge)
                edge_id_counter += 1
        
        # Calculate network summary
        total_projects = len(project_map)
        total_agencies = len(agency_nodes)
        total_states = len(state_nodes)
        total_sectors = len(sector_nodes)
        
        # Calculate high-risk projects
        high_risk_count = sum(
            1 for node in nodes 
            if node.node_type == "PROJECT" and 
            node.risk_category in [RiskCategory.HIGH, RiskCategory.VERY_HIGH, RiskCategory.CRITICAL]
        )
        
        # If project_id is specified, filter to focus on that project's network
        if project_id and project_id in project_map:
            # Get the project's immediate connections
            proj_data = project_map[project_id]
            connected_ids = {project_id}
            
            # Add agency node if exists
            if proj_data["agency"] in agency_nodes:
                connected_ids.add(agency_nodes[proj_data["agency"]])
            
            # Add state node if exists
            if proj_data["state"] in state_nodes:
                connected_ids.add(state_nodes[proj_data["state"]])
            
            # Add sector node if exists
            if proj_data["sector"] in sector_nodes:
                connected_ids.add(sector_nodes[proj_data["sector"]])
            
            # Add other projects sharing the same agency/state/sector
            for other_proj_id, other_proj_data in project_map.items():
                if other_proj_id == project_id:
                    continue
                
                # Same agency
                if (other_proj_data["agency"] == proj_data["agency"] and 
                    proj_data["agency"] in agency_nodes):
                    connected_ids.add(other_proj_id)
                
                # Same state
                if (other_proj_data["state"] == proj_data["state"] and 
                    proj_data["state"] in state_nodes):
                    connected_ids.add(other_proj_id)
                
                # Same sector
                if (other_proj_data["sector"] == proj_data["sector"] and 
                    proj_data["sector"] in sector_nodes):
                    connected_ids.add(other_proj_id)
            
            # Filter nodes and edges
            nodes = [n for n in nodes if n.id in connected_ids]
            edges = [e for e in edges if e.source in connected_ids and e.target in connected_ids]
        
        return NetworkResponse(
            available=True,
            message="Network constructed from project data.",
            nodes=nodes,
            edges=edges,
            metadata={
                "total_projects": total_projects,
                "total_agencies": total_agencies,
                "total_states": total_states,
                "total_sectors": total_sectors,
                "high_risk_projects": high_risk_count,
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "focused_project": project_id,
                "data_source": "REAL_PAIMANA"
            }
        )
        
    except Exception as exc:
        logger.error("Failed to build network: %s", exc)
        return NetworkResponse(
            available=False,
            message=f"Failed to build network: {str(exc)}",
            nodes=[],
            edges=[]
        )
    finally:
        session.close()


def calculate_blast_radius(
    project_id: str,
    depth: int = 2,
    relationship_types: list[str] | None = None,
    risk_threshold: str = "HIGH"
) -> dict[str, Any]:
    """Calculate network reach (blast radius) from a project.
    
    This is a graph reachability analysis, not an impact propagation model.
    It identifies which nodes are reachable within N hops.
    
    Args:
        project_id: Origin project ID
        depth: Maximum hop distance (1, 2, or 3)
        relationship_types: Filter by relationship types (None = all)
        risk_threshold: Filter by risk threshold (ALL, HIGH, VERY_HIGH, CRITICAL)
    
    Returns:
        Dict with affected nodes, projects, agencies, sectors, states, and paths.
    """
    network = build_project_network(project_id)
    
    if not network.available:
        return {
            "available": False,
            "message": network.message,
            "origin_project": project_id,
            "affected_nodes": [],
            "affected_projects": [],
            "affected_agencies": [],
            "affected_sectors": [],
            "affected_states": [],
            "dependency_paths": []
        }
    
    # Build adjacency list
    adj = defaultdict(list)
    for edge in network.edges:
        if relationship_types and edge.relationship_type not in relationship_types:
            continue
        adj[edge.source].append((edge.target, edge.relationship_type))
        adj[edge.target].append((edge.source, edge.relationship_type))
    
    # BFS traversal with depth limit
    visited = set()
    queue = [(project_id, 0)]  # (node_id, depth)
    affected_nodes = []
    dependency_paths = []
    
    while queue:
        node_id, current_depth = queue.pop(0)
        
        if node_id in visited or current_depth > depth:
            continue
        
        visited.add(node_id)
        affected_nodes.append(node_id)
        
        for neighbor, rel_type in adj[node_id]:
            if neighbor not in visited:
                queue.append((neighbor, current_depth + 1))
                dependency_paths.append({
                    "from": node_id,
                    "to": neighbor,
                    "relationship": rel_type,
                    "depth": current_depth + 1
                })
    
    # Categorize affected nodes
    affected_projects = []
    affected_agencies = []
    affected_sectors = []
    affected_states = []
    
    risk_threshold_map = {
        "ALL": None,
        "HIGH": RiskCategory.HIGH,
        "VERY_HIGH": RiskCategory.VERY_HIGH,
        "CRITICAL": RiskCategory.CRITICAL
    }
    threshold = risk_threshold_map.get(risk_threshold, None)
    
    for node in network.nodes:
        if node.id not in visited:
            continue
        
        # Apply risk filter
        if threshold and node.risk_category:
            # Include if risk is at or above threshold
            risk_order = [RiskCategory.LOW, RiskCategory.MODERATE, RiskCategory.HIGH, 
                        RiskCategory.VERY_HIGH, RiskCategory.CRITICAL]
            if risk_order.index(node.risk_category) < risk_order.index(threshold):
                continue
        
        if node.node_type == "PROJECT":
            affected_projects.append(node.id)
        elif node.node_type == "AGENCY":
            affected_agencies.append(node.id)
        elif node.node_type == "SECTOR":
            affected_sectors.append(node.id)
        elif node.node_type == "STATE":
            affected_states.append(node.id)
    
    return {
        "available": True,
        "origin_project": project_id,
        "depth": depth,
        "relationship_types": relationship_types or ["ALL"],
        "risk_threshold": risk_threshold,
        "affected_nodes": affected_nodes,
        "affected_projects": affected_projects,
        "affected_agencies": affected_agencies,
        "affected_sectors": affected_sectors,
        "affected_states": affected_states,
        "dependency_paths": dependency_paths,
        "metadata": {
            "total_affected": len(affected_nodes),
            "direct_connections": len([n for n in adj.get(project_id, [])]),
            "note": "This is network reachability analysis, not impact propagation."
        }
    }
