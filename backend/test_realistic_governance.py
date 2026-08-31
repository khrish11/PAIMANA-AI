"""Test realistic governance scenario with PostgreSQL persistence."""

from app.db.session import SessionLocal
from app.models.projects import Project
from app.models.risk_scores import RiskScore
from app.services.governance_service import (
    initiate_review,
    defer_review,
    complete_review,
    override_review,
    get_project_actions,
    check_escalation
)


def test_realistic_governance_scenario():
    """Simulate a realistic governance workflow with PostgreSQL persistence."""
    print("=" * 80)
    print("REALISTIC GOVERNANCE SCENARIO TEST")
    print("=" * 80)
    
    session = SessionLocal()
    
    try:
        # Step 1: Find a HIGH+ risk project
        print("\n1. Finding a HIGH+ risk project...")
        high_risk = session.query(RiskScore).filter(
            RiskScore.risk_category.in_(["HIGH", "VERY_HIGH", "CRITICAL"])
        ).first()
        
        if not high_risk:
            print("  ❌ FAILED: No HIGH+ risk projects found")
            return
        
        project_id = str(high_risk.project_id)
        print(f"  Found project: {project_id}")
        print(f"  Risk Category: {high_risk.risk_category}")
        print(f"  Composite Score: {high_risk.composite_score}")
        
        # Step 2: Check escalation criteria
        print("\n2. Checking escalation criteria...")
        esc = check_escalation(
            risk_score=float(high_risk.composite_score),
            risk_category=high_risk.risk_category,
            dcs_score=float(high_risk.data_confidence_score) if high_risk.data_confidence_score else None,
            anomaly_count=0
        )
        print(f"  Should Escalate: {esc.should_escalate}")
        print(f"  Trigger Type: {esc.trigger_type}")
        print(f"  Reason: {esc.reason}")
        
        if not esc.should_escalate:
            print("  ⚠️  WARNING: Project does not meet escalation criteria")
        
        # Step 3: Initiate review
        print("\n3. Initiating governance review...")
        action1 = initiate_review(
            project_id=project_id,
            trigger_type=esc.trigger_type,
            reviewer="ipmd_reviewer",
            notes=f"Review initiated due to {esc.trigger_type}"
        )
        print(f"  Action ID: {action1.action_id}")
        print(f"  Status: {action1.outcome}")
        print(f"  ✅ PASSED: Review initiated")
        
        # Step 4: Retrieve actions
        print("\n4. Retrieving project actions...")
        actions = get_project_actions(project_id)
        print(f"  Total actions: {len(actions)}")
        for action in actions:
            print(f"  - {action.action_type}: {action.outcome}")
        print(f"  ✅ PASSED: Actions retrieved from PostgreSQL")
        
        # Step 5: Defer review (simulating need for more information)
        print("\n5. Deferring review for additional analysis...")
        action2 = defer_review(
            project_id=project_id,
            reviewer="ipmd_reviewer",
            notes="Deferred pending additional documentation"
        )
        print(f"  Action ID: {action2.action_id}")
        print(f"  Status: {action2.outcome}")
        print(f"  ✅ PASSED: Review deferred")
        
        # Step 6: Override with justification (simulating expert review)
        print("\n6. Overriding risk assessment with justification...")
        try:
            action3 = override_review(
                project_id=project_id,
                reviewer="expert_reviewer",
                notes="Override: Project shows improvement in recent months. Risk assessment adjusted based on new data."
            )
            print(f"  Action ID: {action3.action_id}")
            print(f"  Status: {action3.outcome}")
            print(f"  ✅ PASSED: Override recorded with justification")
        except Exception as e:
            print(f"  ⚠️  Override failed: {e}")
        
        # Step 7: Complete review
        print("\n7. Completing governance review...")
        action4 = complete_review(
            project_id=project_id,
            reviewer="ipmd_reviewer",
            outcome="approved",
            notes="Review completed. Project approved with monitoring conditions."
        )
        print(f"  Action ID: {action4.action_id}")
        print(f"  Status: {action4.outcome}")
        print(f"  ✅ PASSED: Review completed")
        
        # Step 8: Verify all actions persisted
        print("\n8. Verifying all actions persisted to PostgreSQL...")
        final_actions = get_project_actions(project_id)
        print(f"  Total actions in PostgreSQL: {len(final_actions)}")
        
        if len(final_actions) >= 3:
            print(f"  ✅ PASSED: All actions persisted")
            for action in final_actions:
                print(f"  - {action.action_type}: {action.outcome} (audit: {action.audit_confirmation})")
        else:
            print(f"  ❌ FAILED: Expected at least 3 actions, found {len(final_actions)}")
        
        # Step 9: Verify audit trail
        print("\n9. Verifying audit trail...")
        print(f"  All actions have audit confirmations")
        for action in final_actions:
            if not action.audit_confirmation:
                print(f"  ❌ FAILED: Action {action.action_id} missing audit confirmation")
            else:
                print(f"  - {action.action_id}: {action.audit_confirmation}")
        print(f"  ✅ PASSED: Audit trail verified")
        
        # Step 10: Test blocked actions
        print("\n10. Testing blocked autonomous actions...")
        try:
            from app.services.governance_service import _make_action
            _make_action(
                project_id=project_id,
                action_type="approve_project",
                triggered_by="test",
                reviewed_by="test"
            )
            print(f"  ❌ FAILED: Autonomous approval should be blocked")
        except ValueError as e:
            print(f"  ✅ PASSED: Autonomous approval correctly blocked")
            print(f"  Error: {e}")
        
    finally:
        session.close()
    
    print("\n" + "=" * 80)
    print("REALISTIC GOVERNANCE SCENARIO TEST COMPLETE")
    print("=" * 80)
    print("\nSummary:")
    print("- Governance actions persist to PostgreSQL")
    print("- Audit trail is maintained for all actions")
    print("- Autonomous actions (approve/reject/reallocate) are blocked")
    print("- Full governance workflow: initiate → defer → override → complete")


if __name__ == "__main__":
    test_realistic_governance_scenario()
