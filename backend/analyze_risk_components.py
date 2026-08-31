"""Analyze risk components distribution from database."""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import SessionLocal
from app.models.risk_scores import RiskScore


def analyze_risk_components():
    """Analyze distribution of risk components (cost, schedule, progress, governance)."""
    print("=" * 80)
    print("RISK COMPONENTS DISTRIBUTION ANALYSIS")
    print("=" * 80)
    
    session = SessionLocal()
    
    try:
        # Get all risk scores
        query = session.query(RiskScore).filter(
            RiskScore.composite_score.isnot(None)
        ).all()
        
        if not query:
            print("No risk scores found in database")
            return
        
        print(f"\nTotal risk score records: {len(query)}")
        
        # Extract component values
        cost_risk = [float(r.cost_risk) if r.cost_risk else 0.0 for r in query]
        schedule_risk = [float(r.schedule_risk) if r.schedule_risk else 0.0 for r in query]
        progress_anomaly = [float(r.progress_anomaly_score) if r.progress_anomaly_score else 0.0 for r in query]
        governance_risk = [float(r.governance_risk) if r.governance_risk else 0.0 for r in query]
        composite = [float(r.composite_score) for r in query]
        
        import statistics
        
        # Statistics for each component
        components = [
            ("Cost Risk", cost_risk),
            ("Schedule Risk", schedule_risk),
            ("Progress Anomaly", progress_anomaly),
            ("Governance Risk", governance_risk),
            ("Composite Score", composite),
        ]
        
        print(f"\nComponent Statistics:")
        print("-" * 80)
        
        for name, values in components:
            mean_val = statistics.mean(values)
            median_val = statistics.median(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
            min_val = min(values)
            max_val = max(values)
            
            print(f"\n{name}:")
            print(f"  Mean: {mean_val:.2f}")
            print(f"  Median: {median_val:.2f}")
            print(f"  Std Dev: {std_val:.2f}")
            print(f"  Min: {min_val:.2f}")
            print(f"  Max: {max_val:.2f}")
        
        # Check for zero values (indicates placeholder/default)
        print(f"\nZero Value Analysis:")
        print("-" * 80)
        
        zero_counts = {
            "Cost Risk": sum(1 for v in cost_risk if v == 0),
            "Schedule Risk": sum(1 for v in schedule_risk if v == 0),
            "Progress Anomaly": sum(1 for v in progress_anomaly if v == 0),
            "Governance Risk": sum(1 for v in governance_risk if v == 0),
        }
        
        for name, count in zero_counts.items():
            pct = count / len(query) * 100
            print(f"{name}: {count} zero values ({pct:.1f}%)")
        
        # Distribution by risk category
        print(f"\nRisk Category Distribution:")
        print("-" * 80)
        
        category_dist = session.query(
            RiskScore.risk_category,
            func.count(RiskScore.score_id)
        ).group_by(RiskScore.risk_category).all()
        
        for category, count in category_dist:
            pct = count / len(query) * 100
            print(f"{category}: {count} ({pct:.1f}%)")
        
        # Sample records with high composite scores
        print(f"\nSample High Risk Records (Composite > 50):")
        print("-" * 80)
        
        high_risk = [r for r in query if r.composite_score and r.composite_score > 50]
        for r in high_risk[:5]:
            print(f"Project ID: {r.project_id}")
            print(f"  Composite: {r.composite_score:.2f}")
            print(f"  Cost Risk: {r.cost_risk:.2f}" if r.cost_risk else "  Cost Risk: N/A")
            print(f"  Schedule Risk: {r.schedule_risk:.2f}" if r.schedule_risk else "  Schedule Risk: N/A")
            print(f"  Progress Anomaly: {r.progress_anomaly_score:.2f}" if r.progress_anomaly_score else "  Progress Anomaly: N/A")
            print(f"  Governance Risk: {r.governance_risk:.2f}" if r.governance_risk else "  Governance Risk: N/A")
            print(f"  Category: {r.risk_category}")
            print()
        
    finally:
        session.close()


if __name__ == "__main__":
    analyze_risk_components()
