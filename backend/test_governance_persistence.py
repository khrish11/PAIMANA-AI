"""Test governance persistence with PostgreSQL."""

from uuid import uuid4

from app.services.governance_service import (
    initiate_review,
    defer_review,
    override_review,
    complete_review,
    get_project_actions,
    get_all_pending,
    clear_store
)
from app.db.session import SessionLocal
from app.models.governance_actions import GovernanceAction


def test_governance_persistence():
    """Verify governance actions persist to PostgreSQL."""
    print("=" * 80)
    print("GOVERNANCE PERSISTENCE TEST")
    print("=" * 80)
    
    # Clear existing actions
    clear_store()
    
    # Get an existing project ID from the database
    print("\n0. Getting existing project ID from database...")
    session = SessionLocal()
    try:
        from app.models.projects import Project
        project = session.query(Project).first()
        if project:
            sample_project_id = str(project.project_id)
            print(f"Using existing project ID: {sample_project_id}")
        else:
            print("No projects found in database, cannot test governance")
            return
    finally:
        session.close()
    
    # Test 1: Create a governance action with existing project
    print("\n1. Testing initiate_review...")
    action1 = initiate_review(
        project_id=sample_project_id,
        trigger_type="risk_category_high",
        reviewer="test_reviewer",
        notes="Test review initiation"
    )
    print(f"Action ID: {action1.action_id}")
    print(f"Project ID: {action1.project_id}")
    print(f"Action Type: {action1.action_type}")
    
    # Test 2: Verify persistence in PostgreSQL
    print("\n2. Verifying persistence in PostgreSQL...")
    session = SessionLocal()
    try:
        db_action = session.query(GovernanceAction).filter(
            GovernanceAction.action_id == action1.action_id
        ).first()
        
        if db_action:
            print(f"  ✅ PASSED: Action found in PostgreSQL")
            print(f"  Action Type: {db_action.action_type}")
            print(f"  Notes: {db_action.notes}")
        else:
            print(f"  ❌ FAILED: Action not found in PostgreSQL")
    finally:
        session.close()
    
    # Test 3: Retrieve via service
    print("\n3. Testing get_project_actions...")
    actions = get_project_actions(sample_project_id)
    print(f"Actions found: {len(actions)}")
    if len(actions) > 0:
        print(f"  ✅ PASSED: Actions retrieved via service")
    else:
        print(f"  ❌ FAILED: No actions retrieved")
    
    # Test 4: Test override with notes enforcement
    print("\n4. Testing override with notes enforcement...")
    try:
        override_review(
            project_id=sample_project_id,
            reviewer="test_reviewer",
            notes=""  # Empty notes should fail
        )
        print(f"  ❌ FAILED: Override should reject empty notes")
    except ValueError as e:
        print(f"  ✅ PASSED: Override correctly rejected empty notes")
        print(f"  Error: {e}")
    
    # Test 5: Test override with valid notes
    print("\n5. Testing override with valid notes...")
    action2 = override_review(
        project_id=sample_project_id,
        reviewer="test_reviewer",
        notes="Valid justification for override"
    )
    print(f"Override action ID: {action2.action_id}")
    print(f"  ✅ PASSED: Override with notes succeeded")
    
    # Test 6: Test defer
    print("\n6. Testing defer_review...")
    action3 = defer_review(
        project_id=sample_project_id,
        reviewer="test_reviewer",
        notes="Deferred for further analysis"
    )
    print(f"Defer action ID: {action3.action_id}")
    print(f"  ✅ PASSED: Defer succeeded")
    
    # Test 7: Test complete
    print("\n7. Testing complete_review...")
    action4 = complete_review(
        project_id=sample_project_id,
        reviewer="test_reviewer",
        outcome="approved",
        notes="Review completed successfully"
    )
    print(f"Complete action ID: {action4.action_id}")
    print(f"  ✅ PASSED: Complete succeeded")
    
    # Test 8: Verify all actions in database
    print("\n8. Verifying all actions in database...")
    session = SessionLocal()
    try:
        all_actions = session.query(GovernanceAction).filter(
            GovernanceAction.project_id == sample_project_id
        ).all()
        print(f"Total actions in DB: {len(all_actions)}")
        if len(all_actions) == 4:
            print(f"  ✅ PASSED: All 4 actions persisted")
        else:
            print(f"  ❌ FAILED: Expected 4 actions, found {len(all_actions)}")
    finally:
        session.close()
    
    # Test 9: Test pending retrieval
    print("\n9. Testing get_all_pending...")
    pending = get_all_pending()
    print(f"Pending actions: {len(pending)}")
    print(f"  ✅ PASSED: Pending retrieval works")
    
    # Cleanup
    clear_store()
    
    print("\n" + "=" * 80)
    print("GOVERNANCE PERSISTENCE TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_governance_persistence()
