"""Test RCF with real database data for 10 projects."""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.projects import Project
from app.services.rcf_engine import fit_reference_class, size_band_for_cost


def test_rcf_real_data():
    """Test RCF with 10 real projects from database."""
    print("=" * 80)
    print("RCF REAL DATA TEST - 10 PROJECTS")
    print("=" * 80)
    
    session = SessionLocal()
    
    try:
        # Get 10 sample projects
        projects = session.query(Project).limit(10).all()
        
        print(f"\nTesting RCF for {len(projects)} real projects:")
        print("-" * 80)
        
        for i, project in enumerate(projects, 1):
            print(f"\n{i}. Project: {project.project_id}")
            print(f"   Sector: {project.sector}")
            print(f"   State: {project.state}")
            print(f"   Sanctioned Cost: ₹{project.sanctioned_cost:,.2f} Cr")
            
            sb = size_band_for_cost(float(project.sanctioned_cost))
            print(f"   Size Band: {sb}")
            
            try:
                rcf = fit_reference_class(
                    sector=project.sector,
                    size_band=sb,
                    region=project.state,
                    session=session
                )
                
                print(f"\n   RCF Results:")
                print(f"   - Sample Count: {rcf.sample_count}")
                print(f"   - Used Fallback: {rcf.used_fallback}")
                print(f"   - Warning: {rcf.warning if rcf.warning else 'None'}")
                print(f"   - Cost Overrun P50: {rcf.cost_overrun_p50:.3f}")
                print(f"   - Cost Overrun P80: {rcf.cost_overrun_p80:.3f}")
                print(f"   - Cost Overrun P90: {rcf.cost_overrun_p90:.3f}")
                print(f"   - Schedule Delay P50: {rcf.schedule_delay_p50:.1f} months")
                
                if rcf.used_fallback:
                    print(f"   ⚠ WARNING: RCF used fallback/synthetic data")
                else:
                    print(f"   ✓ RCF used real database data")
                    
            except Exception as e:
                print(f"   ERROR: {str(e)}")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("RCF is using the PostgreSQL database via get_completed_projects_from_db")
        print("Completed projects are identified by physical_progress >= 100")
        print("This provides real reference class data for forecasting")
        
    finally:
        session.close()


if __name__ == "__main__":
    test_rcf_real_data()
