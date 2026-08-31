"""Test governance queue - verify HIGH+ projects appear."""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.risk_scores import RiskScore
from app.models.governance_actions import GovernanceAction
from app.services.governance_service import check_escalation


def test_governance_queue():
    """Verify HIGH+ risk projects appear in governance queue."""
    print("=" * 80)
    print("GOVERNANCE QUEUE TEST - HIGH+ PROJECTS")
    print("=" * 80)
    
    session = SessionLocal()
    
    try:
        # Get HIGH+ risk projects
        high_risk_projects = session.query(RiskScore).filter(
            RiskScore.risk_category.in_(["HIGH", "VERY_HIGH", "CRITICAL"])
        ).all()
        
        print(f"\nHIGH+ Risk Projects in Database:")
        print("-" * 80)
        print(f"Total HIGH+ projects: {len(high_risk_projects)}")
        
        # Count by category
        from collections import Counter
        category_counts = Counter([r.risk_category for r in high_risk_projects])
        for category, count in category_counts.items():
            print(f"  {category}: {count}")
        
        # Check escalation criteria for sample projects
        print(f"\nEscalation Check for Sample HIGH+ Projects:")
        print("-" * 80)
        
        for i, risk in enumerate(high_risk_projects[:5]):
            check = check_escalation(
                risk_score=float(risk.composite_score),
                risk_category=risk.risk_category,
                dcs_score=float(risk.data_confidence_score) if risk.data_confidence_score else None,
            )
            
            print(f"\nProject: {risk.project_id}")
            print(f"  Risk Category: {risk.risk_category}")
            print(f"  Composite Score: {risk.composite_score:.2f}")
            print(f"  DCS Score: {risk.data_confidence_score:.2f}" if risk.data_confidence_score else "  DCS Score: N/A")
            print(f"  Should Escalate: {check.should_escalate}")
            print(f"  Trigger Type: {check.trigger_type}")
            print(f"  Reason: {check.reason}")
        
        # Check governance actions table
        governance_actions = session.query(GovernanceAction).all()
        
        print(f"\nGovernance Actions in Database:")
        print("-" * 80)
        print(f"Total governance actions: {len(governance_actions)}")
        
        if governance_actions:
            # Count by action type
            action_counts = Counter([a.action_type for a in governance_actions])
            print(f"\nAction Types:")
            for action_type, count in action_counts.items():
                print(f"  {action_type}: {count}")
            
            # Sample actions
            print(f"\nSample Governance Actions:")
            for action in governance_actions[:5]:
                print(f"  Action ID: {action.action_id}")
                print(f"    Project: {action.project_id}")
                print(f"    Type: {action.action_type}")
                print(f"    Outcome: {action.outcome}")
                print(f"    Timestamp: {action.timestamp}")
                print()
        else:
            print("No governance actions found in database")
            print("Note: Governance service uses in-memory store for demo")
            print("PostgreSQL model exists but may not be populated")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"HIGH+ risk projects: {len(high_risk_projects)}")
        print(f"All HIGH+ projects should escalate per check_escalation logic")
        print(f"Governance actions in PostgreSQL: {len(governance_actions)}")
        print(f"\nEscalation criteria:")
        print(f"  - Risk category in HIGH, VERY_HIGH, CRITICAL")
        print(f"  - Composite score >= 70")
        print(f"  - Anomaly count >= 3")
        print(f"  - DCS score < 40")
        
    finally:
        session.close()


if __name__ == "__main__":
    test_governance_queue()
