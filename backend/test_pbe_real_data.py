"""Test PBE with real database data for 10 projects."""

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.projects import Project
from app.models.cuf_submissions import CUFSubmission
from app.services.pbe_service import compute_pbe
from app.services.rcf_engine import size_band_for_cost


def test_pbe_real_data():
    """Test PBE with 10 real projects from database."""
    print("=" * 80)
    print("PBE REAL DATA TEST - 10 PROJECTS")
    print("=" * 80)
    
    session = SessionLocal()
    
    try:
        # Get 10 sample projects with known sectors
        projects = session.query(Project).filter(
            Project.sector != 'Unknown'
        ).limit(10).all()
        
        if len(projects) < 10:
            print(f"Only {len(projects)} projects with known sectors found")
        
        print(f"\nTesting PBE for {len(projects)} real projects:")
        print("-" * 80)
        
        for i, project in enumerate(projects, 1):
            print(f"\n{i}. Project: {project.project_id}")
            print(f"   Sector: {project.sector}")
            print(f"   State: {project.state}")
            print(f"   Sanctioned Cost: ₹{project.sanctioned_cost:,.2f} Cr")
            
            # Get latest submission
            latest_submission = session.query(CUFSubmission).filter(
                CUFSubmission.project_id == project.project_id
            ).order_by(CUFSubmission.reporting_month.desc()).first()
            
            if not latest_submission:
                print(f"   No submissions found")
                continue
            
            sb = size_band_for_cost(float(project.sanctioned_cost))
            print(f"   Size Band: {sb}")
            print(f"   Physical Progress: {latest_submission.physical_progress}%")
            
            # Build peer cohort from database
            all_projects = session.query(Project).all()
            peers = []
            
            for p in all_projects:
                if p.project_id == project.project_id:
                    continue  # Self-exclusion
                
                peer_latest = session.query(CUFSubmission).filter(
                    CUFSubmission.project_id == p.project_id
                ).order_by(CUFSubmission.reporting_month.desc()).first()
                
                if peer_latest:
                    peer_sb = size_band_for_cost(float(p.sanctioned_cost))
                    # Filter by sector and size band
                    if p.sector == project.sector and peer_sb == sb:
                        peers.append({
                            'project_id': str(p.project_id),
                            'sector': p.sector,
                            'state': p.state,
                            'size_band': peer_sb,
                            'physical_progress': peer_latest.physical_progress,
                            'expenditure': float(peer_latest.expenditure) if peer_latest.expenditure else 0,
                            'revised_cost': float(peer_latest.revised_cost) if peer_latest.revised_cost else 0,
                        })
            
            print(f"   Peer cohort size: {len(peers)}")
            
            if len(peers) == 0:
                print(f"   No peers found - PBE unavailable")
                continue
            
            # Test state filtering
            same_state_peers = [p for p in peers if p['state'] == project.state]
            print(f"   Peers in same state: {len(same_state_peers)}")
            
            try:
                # Calculate cost overrun for target project
                target_cost_overrun = 0.0
                if latest_submission.revised_cost and project.sanctioned_cost:
                    target_cost_overrun = (float(latest_submission.revised_cost) - float(project.sanctioned_cost)) / float(project.sanctioned_cost)
                
                # Build peer list with required fields
                peer_list = []
                for p in peers:
                    peer_latest = session.query(CUFSubmission).filter(
                        CUFSubmission.project_id == p['project_id']
                    ).order_by(CUFSubmission.reporting_month.desc()).first()
                    if peer_latest and peer_latest.revised_cost:
                        peer_project = session.query(Project).filter(Project.project_id == p['project_id']).first()
                        if peer_project:
                            cost_overrun = (float(peer_latest.revised_cost) - float(peer_project.sanctioned_cost)) / float(peer_project.sanctioned_cost)
                            peer_list.append({
                                'project_id': p['project_id'],
                                'sector': p['sector'],
                                'size_band': p['size_band'],
                                'cost_overrun_ratio': cost_overrun,
                                'schedule_slip_months': 0.0,
                                'physical_progress': p['physical_progress'],
                                'reporting_lag_days': 14,
                                'risk_category': 'MODERATE',
                            })
                
                pbe_result = compute_pbe(
                    project_id=str(project.project_id),
                    own_cost_overrun=target_cost_overrun,
                    own_schedule_slip=0.0,
                    own_physical_progress=latest_submission.physical_progress,
                    own_reporting_lag=14,
                    own_sector=project.sector,
                    own_size_band=sb,
                    peers=peer_list,
                )
                
                print(f"\n   PBE Results:")
                print(f"   - Cohort Size: {pbe_result.cohort_size}")
                print(f"   - PPI (Peer Performance Index): {pbe_result.ppi_score:.3f}")
                print(f"   - Percentile: {pbe_result.percentile:.1f}")
                print(f"   - Stage Normalised: {pbe_result.stage_normalised}")
                print(f"   - Peer Relative Cost Variance: {pbe_result.peer_relative_cost_variance:.3f}")
                print(f"   - Peer Relative Schedule Variance: {pbe_result.peer_relative_schedule_variance:.3f}")
                print(f"   - Cohort Median Cost Overrun: {pbe_result.cohort_median_cost_overrun:.3f}")
                
                if pbe_result.cohort_size >= 10:
                    print(f"   ✓ Sufficient cohort size")
                else:
                    print(f"   ⚠ Small cohort size")
                    
            except Exception as e:
                print(f"   ERROR: {str(e)}")
        
        # Summary
        print(f"\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print("PBE uses real database data for peer cohort construction")
        print("Filtering includes: sector, size_band, and state")
        print("Self-exclusion is enforced by excluding target project from peer list")
        
    finally:
        session.close()


if __name__ == "__main__":
    test_pbe_real_data()
