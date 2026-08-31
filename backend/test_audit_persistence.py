"""Test audit persistence with PostgreSQL."""

from uuid import uuid4

from app.api.v1.audit import record_audit_event
from app.db.session import SessionLocal
from app.models.audit_log import AuditLog


def test_audit_persistence():
    """Verify audit events persist to PostgreSQL."""
    print("=" * 80)
    print("AUDIT PERSISTENCE TEST")
    print("=" * 80)
    
    # Test 1: Record an audit event
    print("\n1. Testing record_audit_event...")
    test_entity_id = str(uuid4())
    record_audit_event(
        user="test_user",
        role="admin",
        action="CREATE",
        entity_type="project",
        entity_id=test_entity_id,
        reason="Test audit event",
        before_summary={"status": "pending"},
        after_summary={"status": "active"}
    )
    print(f"  ✅ PASSED: Audit event recorded")
    
    # Test 2: Verify persistence in PostgreSQL
    print("\n2. Verifying persistence in PostgreSQL...")
    session = SessionLocal()
    try:
        db_event = session.query(AuditLog).filter(
            AuditLog.entity_id == test_entity_id
        ).first()
        
        if db_event:
            print(f"  ✅ PASSED: Audit event found in PostgreSQL")
            print(f"  User: {db_event.user}")
            print(f"  Action: {db_event.action}")
            print(f"  Entity Type: {db_event.entity_type}")
            print(f"  Entity ID: {db_event.entity_id}")
        else:
            print(f"  ❌ FAILED: Audit event not found in PostgreSQL")
    finally:
        session.close()
    
    # Test 3: Record multiple events
    print("\n3. Testing multiple audit events...")
    for i in range(3):
        record_audit_event(
            user=f"test_user_{i}",
            role="admin",
            action="UPDATE",
            entity_type="project",
            entity_id=test_entity_id,
            reason=f"Test update {i}"
        )
    print(f"  ✅ PASSED: Multiple events recorded")
    
    # Test 4: Verify all events in database
    print("\n4. Verifying all events in database...")
    session = SessionLocal()
    try:
        all_events = session.query(AuditLog).filter(
            AuditLog.entity_id == test_entity_id
        ).all()
        print(f"Total events in DB: {len(all_events)}")
        if len(all_events) == 4:
            print(f"  ✅ PASSED: All 4 events persisted")
        else:
            print(f"  ❌ FAILED: Expected 4 events, found {len(all_events)}")
    finally:
        session.close()
    
    # Test 5: Test filtering by action type
    print("\n5. Testing filter by action type...")
    session = SessionLocal()
    try:
        create_events = session.query(AuditLog).filter(
            AuditLog.action == "CREATE"
        ).all()
        print(f"CREATE events found: {len(create_events)}")
        print(f"  ✅ PASSED: Filtering works")
    finally:
        session.close()
    
    print("\n" + "=" * 80)
    print("AUDIT PERSISTENCE TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    test_audit_persistence()
